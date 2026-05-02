import re
from pathlib import Path
from datetime import datetime, timezone

from ..config import settings
from .markdown_service import parse_markdown_document

_TOPIC_RULES = [
    ("C 语言", ("c-", "c语言", "指针", "结构体")),
    ("Java", ("java-", "java")),
    ("Python", ("python-", "python")),
    ("Go", ("go-", "go ", "goroutine", "channel")),
    ("Rust", ("rust-", "rust")),
    ("Vue 3", ("vue-", "vue")),
    ("通用基础", ("algorithm-", "算法", "复杂度")),
]


def _read_markdown(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def _title_from_content(file_path: Path, content: str) -> str:
    match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
    return match.group(1).strip() if match else file_path.stem


def _plain_text(markdown: str) -> str:
    text = re.sub(r"```[\s\S]*?```", " ", markdown)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"#{1,6}\s*", " ", text)
    text = re.sub(r"[*_~>\-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _summary_from_content(content: str) -> str:
    text = _plain_text(content)
    return text[:96] + ("..." if len(text) > 96 else "")


def _topic_from_file(file_name: str, title: str) -> str:
    text = f"{file_name} {title}".lower()

    for topic, keywords in _TOPIC_RULES:
        if any(keyword in text for keyword in keywords):
            return topic

    return "其他"


def _knowledge_item(file_path: Path, scope: str = "system") -> dict:
    raw_content = _read_markdown(file_path)
    metadata, content = parse_markdown_document(raw_content)
    title = _title_from_content(file_path, content)

    return {
        "file": file_path.name,
        "title": metadata.get("title") or title,
        "topic": metadata.get("topic") or _topic_from_file(file_path.name, title),
        "level": metadata.get("level") or "beginner",
        "tags": metadata.get("tags") or [],
        "summary": _summary_from_content(content),
        "scope": scope,
    }


def _user_knowledge_dir(user_id: int | None) -> Path | None:
    if user_id is None:
        return None

    path = settings.user_knowledge_dir / f"user_{user_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def list_knowledge_items(user_id: int | None = None) -> list[dict]:
    items = [_knowledge_item(file_path, scope="system") for file_path in sorted(settings.knowledge_dir.glob("*.md"))]
    user_dir = _user_knowledge_dir(user_id)
    if user_dir:
        items.extend(_knowledge_item(file_path, scope="user") for file_path in sorted(user_dir.glob("*.md")))
    return sorted(items, key=lambda item: (item["topic"], item["title"]))


def get_knowledge_item(file_name: str, user_id: int | None = None) -> dict:
    safe_name = Path(file_name).name
    user_dir = _user_knowledge_dir(user_id)
    user_file_path = user_dir / safe_name if user_dir else None
    file_path = user_file_path if user_file_path and user_file_path.exists() else settings.knowledge_dir / safe_name

    if not file_path.exists() or file_path.suffix.lower() != ".md":
        raise ValueError("知识库资料不存在")

    item = _knowledge_item(file_path, scope="user" if user_file_path and file_path == user_file_path else "system")
    _, content = parse_markdown_document(_read_markdown(file_path))
    item["content"] = content
    return item


def create_user_knowledge_item(user_id: int, payload: dict) -> dict:
    title = str(payload.get("title", "")).strip()
    topic = str(payload.get("topic", "")).strip() or "自定义资料"
    level = str(payload.get("level", "")).strip() or "beginner"
    tags = payload.get("tags") or []
    content = str(payload.get("content", "")).strip()

    if not title or not content:
        raise ValueError("title、content 字段不能为空")

    if not isinstance(tags, list):
        tags = [str(tags)]

    safe_stem = _slugify(title) or f"knowledge-{int(datetime.now(timezone.utc).timestamp())}"
    file_name = f"{safe_stem}.md"
    user_dir = _user_knowledge_dir(user_id)
    assert user_dir is not None
    file_path = user_dir / file_name
    suffix = 2

    while file_path.exists():
        file_name = f"{safe_stem}-{suffix}.md"
        file_path = user_dir / file_name
        suffix += 1

    front_matter = "\n".join(
        [
            "---",
            f"title: {title}",
            f"topic: {topic}",
            f"level: {level}",
            f"tags: [{', '.join(str(tag).strip() for tag in tags if str(tag).strip())}]",
            "---",
            "",
        ]
    )
    file_path.write_text(front_matter + content + "\n", encoding="utf-8")
    return get_knowledge_item(file_name, user_id=user_id)


def delete_user_knowledge_item(user_id: int, file_name: str) -> None:
    safe_name = Path(file_name).name
    user_dir = _user_knowledge_dir(user_id)

    if user_dir is None:
        raise ValueError("请先登录后再删除资料")

    file_path = user_dir / safe_name

    if not file_path.exists() or file_path.suffix.lower() != ".md":
        raise ValueError("个人资料不存在")

    # 只允许删除当前用户目录下的 Markdown 文件，避免误删系统知识库资料。
    if file_path.resolve().parent != user_dir.resolve():
        raise ValueError("无权删除该资料")

    file_path.unlink()


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", value.lower(), flags=re.UNICODE)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    return normalized[:48]
