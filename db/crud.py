import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas

TOKEN_LIFETIME_HOURS = 24


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return f"{salt.hex()}:{derived_key.hex()}"


def verify_password(password: str, stored_password_hash: str) -> bool:
    try:
        salt_hex, expected_hash = stored_password_hash.split(":", maxsplit=1)
    except ValueError:
        return False

    salt = bytes.fromhex(salt_hex)
    actual_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()
    return hmac.compare_digest(actual_hash, expected_hash)


def create_user(db: Session, user: schemas.UserCreate):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_auth_token(db: Session, user: models.User):
    expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_LIFETIME_HOURS)
    auth_token = models.AuthToken(
        token=secrets.token_urlsafe(32),
        expires_at=expires_at,
        user_id=user.id,
    )
    db.add(auth_token)
    db.commit()
    db.refresh(auth_token)
    return auth_token


def get_user_by_token(db: Session, token: str):
    auth_token = db.query(models.AuthToken).filter(models.AuthToken.token == token).first()
    if auth_token is None:
        return None

    expires_at = auth_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        db.delete(auth_token)
        db.commit()
        return None

    return auth_token.user


def create_user_post(db: Session, post: schemas.PostCreate, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_post = models.Post(title=post.title, content=post.content, author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()
