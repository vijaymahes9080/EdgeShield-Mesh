"""
EdgeShield Mesh - Security and Sanitization Utilities
"""
import re
import hmac
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Dict, Any
import jwt
import bcrypt

# JWT configuration defaults
SECRET_KEY = "edgeshield-mesh-super-secure-jwt-dev-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12 hours for edge operators

# PII Patterns
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
IP_REGEX = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
MAC_REGEX = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b")

# Prompt Injection Markers
SUSPICIOUS_PROMPT_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are", re.IGNORECASE),
    re.compile(r"new\s+instructions\s*:", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+dan\s+mode", re.IGNORECASE),
    re.compile(r"bypass\s+security\s+controls", re.IGNORECASE),
    re.compile(r"override\s+safety\s+filter", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"<\|im_end\|>", re.IGNORECASE),
    re.compile(r"```python\s*import\s+os\s*;\s*os\.system", re.IGNORECASE),
]


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8")[:72], salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    secret_key: str = SECRET_KEY
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str, secret_key: str = SECRET_KEY) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")


def redact_pii(text: str) -> str:
    """
    Redacts sensitive PII (emails, non-local IP addresses, MAC addresses) from strings.
    """
    if not isinstance(text, str):
        return text
    # Redact emails
    text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
    # Redact MAC addresses
    text = MAC_REGEX.sub("[REDACTED_MAC]", text)
    return text


def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Checks if a piece of text (e.g. telemetry string, device metadata) contains prompt injection attempts.
    Returns (is_injected, rule_matched).
    """
    if not isinstance(text, str):
        return False, ""
    for pattern in SUSPICIOUS_PROMPT_PATTERNS:
        if pattern.search(text):
            return True, pattern.pattern
    return False, ""


def sanitize_untrusted_input(text: str, max_length: int = 1000) -> str:
    """
    Strips dangerous control chars, bounds length, and encapsulates untrusted input safely.
    """
    if not isinstance(text, str):
        return str(text)
    # Truncate
    truncated = text[:max_length]
    # Neutralize markdown/system breakout characters
    sanitized = truncated.replace("<|im_start|>", "").replace("<|im_end|>", "")
    return sanitized
