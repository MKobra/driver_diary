import base64
import hashlib
import hmac
import secrets
import time


PASSWORD_ITERATIONS = 310_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, PASSWORD_ITERATIONS
    )
    return f"{PASSWORD_ITERATIONS}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        iterations_text, salt_text, digest_text = password_hash.split("$", 2)
        expected = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            _decode(salt_text),
            int(iterations_text),
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(expected, _decode(digest_text))


def create_session(user_id: str, secret: bytes) -> str:
    payload = f"{user_id}:{int(time.time())}".encode()
    signature = hmac.new(secret, payload, hashlib.sha256).digest()
    return f"{_encode(payload)}.{_encode(signature)}"


def read_session(token: str | None, secret: bytes, max_age: int) -> str | None:
    if not token or "." not in token:
        return None
    payload_text, signature_text = token.split(".", 1)
    try:
        payload = _decode(payload_text)
        signature = _decode(signature_text)
        expected = hmac.new(secret, payload, hashlib.sha256).digest()
        user_id, created_text = payload.decode().split(":", 1)
        created_at = int(created_text)
    except (ValueError, TypeError, UnicodeDecodeError):
        return None
    if not hmac.compare_digest(signature, expected):
        return None
    if time.time() - created_at > max_age:
        return None
    return user_id


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
