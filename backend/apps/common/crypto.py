"""Maxfiy matnlarni (Telegram session) shifrlash. ENCRYPTION_KEY dan Fernet kaliti hosil qilinadi.

Har qanday ENCRYPTION_KEY satridan barqaror Fernet kaliti olamiz (SHA256 -> urlsafe b64),
shunda kalit formatidan qat'i nazar ishlaydi.
"""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet() -> Fernet:
    raw = (settings.ENCRYPTION_KEY or "").encode()
    key = base64.urlsafe_b64encode(hashlib.sha256(raw).digest())
    return Fernet(key)


def encrypt(plaintext: str) -> str:
    if not plaintext:
        return ""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    if not ciphertext:
        return ""
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        # ponytail: eski ochiq (shifrlanmagan) sessiyalar bilan orqaga moslik
        return ciphertext
