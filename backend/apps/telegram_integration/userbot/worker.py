"""Userbot worker — 100+ akkaunt uchun optimallashtirilgan.

Optimizatsiyalar:
- Sharding: har konteyner akkauntlarning bir ulushini oladi (USERBOT_SHARD_*).
- api_id/hash pool: akkauntlarga barqaror taqsimlanadi.
- Keyword-gate: Gemini faqat trigger keyword mos kelsagina chaqiriladi (~90% call tejaladi).
- Tenant cache: mahsulot/triggerlar TTL bilan keshlanadi (har xabarda DB emas).
- Rate-limit: har akkauntga soatiga cheklangan yuborish (ban himoyasi).
- Faqat tasdiqlangan guruhlar (admin_approved) ga yoziladi.
- Javobdan oldin tasodifiy inson-kabi kechikish.
- Sessiya bazadan shifrlangan holda o'qiladi.
"""
import asyncio
import logging
import random
import time

from asgiref.sync import sync_to_async
from django.conf import settings
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from apps.ai_engine.services import get_ai_provider
from apps.products.models import Product
from apps.telegram_integration.models import TelegramChat, TelegramConnection
from apps.triggers.models import TriggerSet

logger = logging.getLogger("userbot")

RELOAD_SECONDS = 30


def _api_pool():
    pool = []
    raw = (settings.TELEGRAM_API_POOL or "").strip()
    for pair in raw.split(","):
        pair = pair.strip()
        if ":" in pair:
            api_id, api_hash = pair.split(":", 1)
            pool.append((int(api_id), api_hash.strip()))
    if not pool and settings.TELEGRAM_API_ID and settings.TELEGRAM_API_HASH:
        pool.append((int(settings.TELEGRAM_API_ID), settings.TELEGRAM_API_HASH))
    return pool


def _stable_hash(value: str) -> int:
    # PYTHONHASHSEED'dan mustaqil, jarayonlararo barqaror
    return int(str(value).replace("-", "")[:12], 16)


class UserbotRunner:
    def __init__(self):
        self._clients: dict[str, TelegramClient] = {}
        self._last_ad: dict[str, float] = {}      # chat_key -> ts
        self._sends: dict[str, list[float]] = {}  # conn_id -> [ts]
        self._cache: dict[str, tuple[float, dict]] = {}  # workspace_id -> (ts, data)
        self._provider = None

    # ---- lifecycle ----
    async def run(self):
        while True:
            pool = _api_pool()
            if not pool:
                logger.warning("TELEGRAM_API_ID/HASH sozlanmagan — userbot kutmoqda.")
                await asyncio.sleep(RELOAD_SECONDS)
                continue
            if self._provider is None:
                self._provider = get_ai_provider()
            for conn in await self._active_connections():
                if conn.id in self._clients:
                    continue
                try:
                    api_id, api_hash = pool[_stable_hash(conn.id) % len(pool)]
                    await self._start_client(conn, api_id, api_hash)
                    logger.info("userbot started: %s", conn.phone)
                except Exception as exc:  # noqa: BLE001
                    logger.exception("userbot start failed for %s: %s", conn.phone, exc)
                    await self._mark_error(conn, str(exc))
            await asyncio.sleep(RELOAD_SECONDS)

    @sync_to_async
    def _active_connections(self):
        conns = TelegramConnection.objects.filter(
            mode="userbot", login_state="active", is_active=True
        ).exclude(session_string="")
        # sharding: shu worker faqat o'z ulushini oladi
        return [
            c for c in conns
            if _stable_hash(c.id) % settings.USERBOT_SHARD_COUNT == settings.USERBOT_SHARD_INDEX
        ]

    @sync_to_async
    def _mark_error(self, conn, message):
        conn.login_state = "error"
        conn.last_error = message[:2000]
        conn.save(update_fields=["login_state", "last_error"])

    async def _start_client(self, conn, api_id, api_hash):
        client = TelegramClient(StringSession(conn.get_session()), api_id, api_hash)
        await client.connect()
        if not await client.is_user_authorized():
            raise RuntimeError("Sessiya yaroqsiz, qayta login kerak.")
        workspace_id = conn.workspace_id
        conn_id = str(conn.id)

        @client.on(events.NewMessage(incoming=True))
        async def handler(event):  # noqa: ANN001
            try:
                text = (event.raw_text or "").strip()
                if not text or not self._can_send(conn_id):
                    return
                if event.is_private:
                    await self._handle_dm(event, workspace_id, conn_id, text)
                elif event.is_group:
                    await self._handle_group(event, workspace_id, conn_id, text)
            except Exception as exc:  # noqa: BLE001
                logger.exception("handler error: %s", exc)

        self._clients[conn.id] = client

    # ---- rate limiting (akkaunt shard'ga bog'langani uchun in-process yetarli) ----
    def _can_send(self, conn_id: str) -> bool:
        now = time.monotonic()
        window = self._sends.setdefault(conn_id, [])
        window[:] = [t for t in window if t > now - 3600]
        return len(window) < settings.USERBOT_MAX_SENDS_PER_HOUR

    def _record_send(self, conn_id: str):
        self._sends.setdefault(conn_id, []).append(time.monotonic())

    async def _reply(self, event, conn_id, text):
        await asyncio.sleep(random.uniform(settings.USERBOT_MIN_DELAY, settings.USERBOT_MAX_DELAY))
        await event.reply(text)
        self._record_send(conn_id)

    # ---- tenant cache (mahsulot + trigger keyword qoidalari) ----
    async def _tenant(self, workspace_id) -> dict:
        now = time.monotonic()
        entry = self._cache.get(workspace_id)
        if entry and now - entry[0] < settings.USERBOT_TENANT_CACHE_TTL:
            return entry[1]
        data = await self._load_tenant(workspace_id)
        self._cache[workspace_id] = (now, data)
        return data

    @sync_to_async
    def _load_tenant(self, workspace_id):
        products = list(Product.objects.filter(workspace_id=workspace_id, status="active")[:20])
        rules = []
        triggers = (
            TriggerSet.objects.filter(workspace_id=workspace_id, enabled=True)
            .select_related("product")
        )
        for t in triggers:
            keywords = [k.lower() for k in (t.positive_keywords or []) if k]
            negative = [k.lower() for k in (t.negative_keywords or []) if k]
            product = t.product or (products[0] if products else None)
            if keywords and product:
                rules.append({"keywords": keywords, "negative": negative, "product": product})
        return {"products": products, "rules": rules}

    def _match_rule(self, tenant, text_lower):
        for rule in tenant["rules"]:
            if any(n in text_lower for n in rule["negative"]):
                continue
            if any(k in text_lower for k in rule["keywords"]):
                return rule
        return None

    @sync_to_async
    def _is_approved_group(self, workspace_id, chat_id):
        return TelegramChat.objects.filter(
            workspace_id=workspace_id,
            telegram_chat_id=str(chat_id),
            monitoring_enabled=True,
            admin_approved=True,
        ).exists()

    # ---- handlers ----
    async def _handle_group(self, event, workspace_id, conn_id, text):
        chat_key = f"{conn_id}:{event.chat_id}"
        if time.monotonic() - self._last_ad.get(chat_key, 0) < settings.USERBOT_GROUP_COOLDOWN:
            return
        tenant = await self._tenant(workspace_id)
        rule = self._match_rule(tenant, text.lower())
        if not rule:  # keyword gate — Gemini'ga bekorga bormaymiz
            return
        if not await self._is_approved_group(workspace_id, event.chat_id):
            return  # ponytail: faqat dashboard'da tasdiqlangan guruhlar; ban xavfini kamaytiradi
        product = rule["product"]
        result = await sync_to_async(self._provider.classify_message)(
            message=text, product=product, consent_status="group_public"
        )
        if result.is_relevant and result.confidence >= 0.6:
            draft = await sync_to_async(self._provider.generate_product_response)(
                message=text, product=product, consent_status="group_public"
            )
            await self._reply(event, conn_id, draft.text)
            self._last_ad[chat_key] = time.monotonic()

    async def _handle_dm(self, event, workspace_id, conn_id, text):
        tenant = await self._tenant(workspace_id)
        rule = self._match_rule(tenant, text.lower())
        product = rule["product"] if rule else (tenant["products"][0] if tenant["products"] else None)
        if not product:
            return
        draft = await sync_to_async(self._provider.generate_product_response)(
            message=text, product=product, consent_status="direct_inquiry"
        )
        await self._reply(event, conn_id, draft.text)


def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.run(UserbotRunner().run())
