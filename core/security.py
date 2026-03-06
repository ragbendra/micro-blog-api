import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-do-not-use-in-prod")
ALGORITHM = "HS256"


def _get_access_token_expire_minutes() -> int:
    try:
        return int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    except ValueError:
        return 30


ACCESS_TOKEN_EXPIRE_MINUTES = _get_access_token_expire_minutes()


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not isinstance(email, str) or not email:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception
