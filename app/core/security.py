from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(data: Dict[str, Any], expires_minutes: int, scope: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "scope": scope})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, extra: Dict[str, Any] | None = None) -> str:
    payload = {"sub": subject}
    if extra:
        payload.update(extra)
    return _create_token(
        payload, settings.access_token_exp_minutes, scope="access_token"
    )


def create_refresh_token(subject: str, extra: Dict[str, Any] | None = None) -> str:
    payload = {"sub": subject}
    if extra:
        payload.update(extra)
    return _create_token(
        payload, settings.refresh_token_exp_minutes, scope="refresh_token"
    )


def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Token inválido") from exc

