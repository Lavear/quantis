from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
from .config import settings


def hash_password(p: str) -> str:
    # bcrypt has a 72-byte input limit; truncate defensively.
    pw = p.encode("utf-8")[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(p: str, h: str) -> bool:
    pw = p.encode("utf-8")[:72]
    return bcrypt.checkpw(pw, h.encode("utf-8"))


def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": expire},
                      settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET,
                             algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
