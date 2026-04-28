import secrets
from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import User


def register_user(username: str, password: str) -> dict:
    username = username.strip()
    password = password.strip()

    if len(username) < 2:
        raise ValueError("用户名至少需要 2 个字符")
    if len(password) < 4:
        raise ValueError("密码至少需要 4 个字符")
    if User.query.filter_by(username=username).first():
        raise ValueError("用户名已存在")

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        token=secrets.token_hex(24),
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


def login_user(username: str, password: str) -> dict:
    user = User.query.filter_by(username=username.strip()).first()

    if not user or not check_password_hash(user.password_hash, password.strip()):
        raise ValueError("用户名或密码错误")

    return user.to_dict()


def get_user_by_token(token: str | None):
    if not token:
        return None

    return User.query.filter_by(token=token.strip()).first()
