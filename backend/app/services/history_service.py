from datetime import datetime, timezone

from sqlalchemy import or_

from ..extensions import db
from ..models import ConversationHistory


def list_history(keyword: str = "", mode: str = "", limit: int = 50, user_id: int | None = None) -> list[dict]:
    query = ConversationHistory.query.filter(ConversationHistory.user_id == user_id)

    if mode:
        query = query.filter(ConversationHistory.mode == mode)

    if keyword:
        like_keyword = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                ConversationHistory.question.ilike(like_keyword),
                ConversationHistory.reply.ilike(like_keyword),
            )
        )

    records = (
        query.order_by(ConversationHistory.created_at.desc())
        .limit(max(1, min(limit, 200)))
        .all()
    )
    return [record.to_dict() for record in records]


def add_history_entry(entry: dict) -> dict:
    record = ConversationHistory(
        user_id=entry.get("userId"),
        mode=entry["mode"],
        mode_label=entry["modeLabel"],
        question=entry["question"],
        reply=entry["reply"],
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(record)
    db.session.commit()
    return record.to_dict()


def clear_history(user_id: int | None = None) -> None:
    ConversationHistory.query.filter(ConversationHistory.user_id == user_id).delete()
    db.session.commit()


def delete_history_entry(record_id: int, user_id: int | None = None) -> None:
    record = ConversationHistory.query.filter_by(id=record_id, user_id=user_id).first()

    if not record:
        raise ValueError("历史会话不存在")

    db.session.delete(record)
    db.session.commit()
