"""Telethon userbot login: telefon + kod (stateless, ikki qadamli).

start_login: kod yuboradi, qisman sessiyani (auth key) saqlaydi.
verify_login: o'sha sessiyani tiklab sign_in qiladi, to'liq session_string qaytaradi.
"""
from django.conf import settings
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession


def _api():
    api_id = settings.TELEGRAM_API_ID
    api_hash = settings.TELEGRAM_API_HASH
    if not api_id or not api_hash:
        raise RuntimeError("TELEGRAM_API_ID/HASH sozlanmagan.")
    return int(api_id), api_hash


async def start_login(phone: str, session_string: str = "") -> dict:
    api_id, api_hash = _api()
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
    await client.connect()
    try:
        sent = await client.send_code_request(phone)
        return {
            "session_string": client.session.save(),
            "phone_code_hash": sent.phone_code_hash,
        }
    finally:
        await client.disconnect()


async def verify_login(phone: str, code: str, phone_code_hash: str, session_string: str, password: str = "") -> dict:
    api_id, api_hash = _api()
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
    await client.connect()
    try:
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        except SessionPasswordNeededError:
            if not password:
                return {"needs_password": True}
            await client.sign_in(password=password)
        me = await client.get_me()
        return {
            "session_string": client.session.save(),
            "user_id": str(me.id),
            "username": me.username or "",
            "needs_password": False,
        }
    finally:
        await client.disconnect()
