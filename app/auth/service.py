from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def register_user(
    db: Session,
    username: str,
    email: str,
    password: str,
) -> User:

    existing_user = db.scalar(
        select(User).where(
            (User.username == username)
            | (User.email == email)
        )
    )

    if existing_user:
        raise ValueError(
            "Username or email already exists."
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role="user",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> User | None:

    user = db.scalar(
        select(User).where(
            User.username == username
        )
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def generate_user_token(user: User) -> str:
    return create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role,
    )