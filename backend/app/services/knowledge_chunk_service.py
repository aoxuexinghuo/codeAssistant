import re
from pathlib import Path

from ..config import settings
from .markdown_service import parse_markdown_document


def clean_markdown(text: str) -> str:
    text = re.sub(r"```[a-zA-Z0-9_-]*\n([\s\S]*?)```", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"#{1,6}\s*", " ", text)
    text = re.sub(r"[*_~>\-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def title_from_markdown(file_path: Path, content: str) -> str:
    match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
    return match.group(1).strip() if match else file_path.stem


def split_text(text: str) -> list[str]:
    chunk_size = settings.rag_chunk_size
    overlap = min(settings.rag_chunk_overlap, max(0, chunk_size // 2))
    cleaned = clean_markdown(text)

    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        chunks.append(cleaned[start:end].strip())

        if end >= len(cleaned):
            break

        start = max(0, end - overlap)

    return [chunk for chunk in chunks if chunk]


def load_knowledge_chunks(user_id: int | None = None, include_all_users: bool = False) -> list[dict]:
    documents: list[dict] = []

    knowledge_dirs: list[tuple[Path, str, int]] = [(settings.knowledge_dir, "system", 0)]
    if user_id is not None:
        user_dir = settings.user_knowledge_dir / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        knowledge_dirs.append((user_dir, "user", user_id))

    if include_all_users:
        for user_dir in sorted(settings.user_knowledge_dir.glob("user_*")):
            if not user_dir.is_dir():
                continue

            try:
                owner_id = int(user_dir.name.replace("user_", "", 1))
            except ValueError:
                continue

            knowledge_dirs.append((user_dir, "user", owner_id))

    seen_dirs: set[Path] = set()
    for knowledge_dir, scope, owner_id in knowledge_dirs:
        resolved_dir = knowledge_dir.resolve()
        if resolved_dir in seen_dirs:
            continue
        seen_dirs.add(resolved_dir)

        for file_path in sorted(knowledge_dir.glob("*.md")):
            raw_content = file_path.read_text(encoding="utf-8")
            metadata, content = parse_markdown_document(raw_content)
            title = metadata.get("title") or title_from_markdown(file_path, content)

            for index, chunk in enumerate(split_text(content), start=1):
                documents.append(
                    {
                        "id": f"{scope}:{owner_id}:{file_path.name}#{index}",
                        "title": title,
                        "file": file_path.name,
                        "chunkIndex": index,
                        "content": chunk,
                        "topic": metadata.get("topic") or "",
                        "level": metadata.get("level") or "",
                        "tags": metadata.get("tags") or [],
                        "scope": scope,
                        "userId": owner_id,
                    }
                )

    return documents
