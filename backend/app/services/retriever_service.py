import json
import re
from pathlib import Path

from ..config import settings
from .embedding_service import tokenize_text


def _clean_markdown(text: str) -> str:
    text = re.sub(r"```[a-zA-Z0-9_-]*\n([\s\S]*?)```", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"#{1,6}\s*", " ", text)
    text = re.sub(r"[*_~>\-]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _title_from_markdown(file_path: Path, content: str) -> str:
    match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
    return match.group(1).strip() if match else file_path.stem


def _split_text(text: str) -> list[str]:
    chunk_size = settings.rag_chunk_size
    overlap = min(settings.rag_chunk_overlap, max(0, chunk_size // 2))
    cleaned = _clean_markdown(text)

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


def rebuild_index() -> dict:
    documents: list[dict] = []

    for file_path in sorted(settings.knowledge_dir.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        title = _title_from_markdown(file_path, content)

        for index, chunk in enumerate(_split_text(content), start=1):
            documents.append(
                {
                    "id": f"{file_path.name}#{index}",
                    "title": title,
                    "file": file_path.name,
                    "chunkIndex": index,
                    "content": chunk,
                    "tokens": sorted(tokenize_text(f"{title} {chunk}")),
                }
            )

    payload = {"documents": documents}
    settings.rag_index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"documentCount": len(documents), "indexPath": str(settings.rag_index_path)}


def _load_index() -> list[dict]:
    if not settings.rag_index_path.exists():
        rebuild_index()

    payload = json.loads(settings.rag_index_path.read_text(encoding="utf-8"))
    return payload.get("documents", [])


def retrieve_documents(question: str, top_k: int | None = None, min_score: float | None = None) -> list[dict]:
    query_tokens = tokenize_text(question)
    score_threshold = settings.rag_min_score if min_score is None else min_score

    if not query_tokens:
        return []

    scored: list[tuple[float, dict]] = []
    for document in _load_index():
        document_tokens = set(document.get("tokens", []))
        matched = query_tokens & document_tokens

        if not matched:
            continue

        score = len(matched) / max(1, len(query_tokens))
        if score < score_threshold:
            continue

        scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)

    results = []
    for score, document in scored[: top_k or settings.rag_top_k]:
        results.append(
            {
                "title": document["title"],
                "file": document["file"],
                "chunkIndex": document["chunkIndex"],
                "content": document["content"],
                "score": round(score, 4),
            }
        )

    return results
