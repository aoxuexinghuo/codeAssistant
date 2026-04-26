import re
from pathlib import Path

from ..config import settings

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


def _knowledge_item(file_path: Path) -> dict:
    content = _read_markdown(file_path)
    title = _title_from_content(file_path, content)

    return {
        "file": file_path.name,
        "title": title,
        "topic": _topic_from_file(file_path.name, title),
        "summary": _summary_from_content(content),
    }


def list_knowledge_items() -> list[dict]:
    items = [_knowledge_item(file_path) for file_path in sorted(settings.knowledge_dir.glob("*.md"))]
    return sorted(items, key=lambda item: (item["topic"], item["title"]))


def get_knowledge_item(file_name: str) -> dict:
    safe_name = Path(file_name).name
    file_path = settings.knowledge_dir / safe_name

    if not file_path.exists() or file_path.suffix.lower() != ".md":
        raise ValueError("知识库资料不存在")

    item = _knowledge_item(file_path)
    item["content"] = _read_markdown(file_path)
    return item
