"""
Unit Tests for Authentication, JWT, and Role-Based Access Control
"""
import pytest
from datetime import timedelta
from packages.shared.models import UserRole
from packages.shared.security import (
    verify_password, get_password_hash, create_access_token, decode_access_token
)


def test_password_hashing():
    pwd = "secure_iot_password_123!"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_token_flow():
    data = {"sub": "operator", "role": UserRole.OPERATOR.value}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=30))
    payload = decode_access_token(token)
    assert payload["sub"] == "operator"
    assert payload["role"] == "operator"
    assert "exp" in payload


def test_expired_token_raises_error():
    data = {"sub": "operator", "role": UserRole.OPERATOR.value}
    # Expired token (-10 seconds)
    token = create_access_token(data=data, expires_delta=timedelta(seconds=-10))
    with pytest.raises(ValueError) as exc:
        decode_access_token(token)
    assert "expired" in str(exc.value).lower()
