import json

from ..config import settings
from .embedding_service import tokenize_text
from .knowledge_chunk_service import load_knowledge_chunks


def rebuild_index() -> dict:
    documents = [
        {
            **document,
            "tokens": sorted(tokenize_text(f"{document['title']} {document['content']}")),
        }
        for document in load_knowledge_chunks()
    ]

    payload = {"documents": documents}
    settings.rag_index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"documentCount": len(documents), "indexPath": str(settings.rag_index_path)}


def _load_index() -> list[dict]:
    if not settings.rag_index_path.exists():
        rebuild_index()

    payload = json.loads(settings.rag_index_path.read_text(encoding="utf-8"))
    return payload.get("documents", [])


def retrieve_documents(question: str, top_k: int | None = None, min_score: float | None = None) -> list[dict]:
    if settings.rag_retriever_type == "vector":
        try:
            from .vector_store_service import search_vector_store

            return search_vector_store(question=question, top_k=top_k, min_score=min_score)
        except Exception as error:
            print("[rag] vector search fallback", {"detail": str(error)})

    return retrieve_documents_by_keyword(question=question, top_k=top_k, min_score=min_score)


def retrieve_documents_by_keyword(question: str, top_k: int | None = None, min_score: float | None = None) -> list[dict]:
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
                "topic": document.get("topic", ""),
                "level": document.get("level", ""),
                "tags": document.get("tags", []),
                "score": round(score, 4),
            }
        )

    return results
