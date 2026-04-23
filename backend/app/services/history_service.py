from datetime import datetime, timezone

from sqlalchemy import or_

from ..extensions import db
from ..models import ConversationHistory


def list_history(keyword: str = "", mode: str = "", limit: int = 50) -> list[dict]:
    query = ConversationHistory.query

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
        mode=entry["mode"],
        mode_label=entry["modeLabel"],
        question=entry["question"],
        reply=entry["reply"],
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(record)
    db.session.commit()
    return record.to_dict()


def clear_history() -> None:
    ConversationHistory.query.delete()
    db.session.commit()
