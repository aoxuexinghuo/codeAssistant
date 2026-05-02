from sqlalchemy import inspect, text

from ..extensions import db


def ensure_lightweight_migrations() -> None:
    """为本地演示环境补齐 create_all 不会自动添加的新增列。"""
    inspector = inspect(db.engine)

    _add_column_if_missing(inspector, "user_profile", "user_id", "INTEGER")
    _add_column_if_missing(inspector, "user_profile", "total_points", "INTEGER DEFAULT 0")
    _add_column_if_missing(inspector, "conversation_history", "user_id", "INTEGER")
    _add_column_if_missing(inspector, "mistake_records", "user_id", "INTEGER")
    _add_column_if_missing(inspector, "mistake_records", "review_status", "VARCHAR(32) DEFAULT 'pending'")
    _add_column_if_missing(inspector, "mistake_records", "review_note", "TEXT DEFAULT ''")
    _add_column_if_missing(inspector, "mistake_records", "review_points", "INTEGER DEFAULT 0")
    _add_column_if_missing(inspector, "mistake_records", "reviewed_at", "DATETIME")
    _add_column_if_missing(inspector, "mistake_records", "mastered_at", "DATETIME")


def _add_column_if_missing(inspector, table_name: str, column_name: str, column_type: str) -> None:
    if not inspector.has_table(table_name):
        return

    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name in columns:
        return

    db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
    db.session.commit()
