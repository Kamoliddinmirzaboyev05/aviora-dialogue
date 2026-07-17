"""Userbot scaling logikasi self-check: shifrlash, keyword-gate, rate-limit."""
from apps.common.crypto import decrypt, encrypt
from apps.telegram_integration.userbot.worker import UserbotRunner, _stable_hash


def test_session_encryption_roundtrip():
    secret = "1BVtsOL...telethon-session-string"
    enc = encrypt(secret)
    assert enc != secret and enc  # ochiq saqlanmaydi
    assert decrypt(enc) == secret


def test_decrypt_plaintext_backward_compat():
    # eski shifrlanmagan qiymatlar buzilmasligi kerak
    assert decrypt("plain-old-value") == "plain-old-value"


def test_stable_hash_is_process_independent():
    # UUID uchun barqaror (sharding to'g'ri ishlashi uchun)
    assert _stable_hash("11111111-2222-3333-4444-555555555555") == int("111111112222", 16)


def test_keyword_gate_matches_and_respects_negatives():
    runner = UserbotRunner()
    p = object()
    tenant = {
        "products": [p],
        "rules": [{"keywords": ["crm kerak", "dastur"], "negative": ["bepul"], "product": p}],
    }
    assert runner._match_rule(tenant, "menga yaxshi crm kerak") is not None
    assert runner._match_rule(tenant, "bepul dastur bormi") is None  # negative bloklaydi
    assert runner._match_rule(tenant, "salom qalaysiz") is None  # keyword yo'q -> Gemini chaqirilmaydi


def test_rate_limit_caps_per_hour(settings):
    settings.USERBOT_MAX_SENDS_PER_HOUR = 2
    runner = UserbotRunner()
    assert runner._can_send("c1")
    runner._record_send("c1")
    runner._record_send("c1")
    assert not runner._can_send("c1")  # limit tugadi
