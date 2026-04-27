import shutil

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from ..config import settings
from .knowledge_chunk_service import load_knowledge_chunks

COLLECTION_NAME = "programming_assistant_knowledge"


def _import_chroma():
    try:
        from langchain_chroma import Chroma

        return Chroma
    except ImportError:
        from langchain_community.vectorstores import Chroma

        return Chroma


def _create_embedding_model() -> OpenAIEmbeddings:
    if not settings.embedding_api_key:
        raise ValueError("缺少 EMBEDDING_API_KEY、LLM_API_KEY 或 DASHSCOPE_API_KEY 环境变量")

    return OpenAIEmbeddings(
        api_key=settings.embedding_api_key,
        base_url=settings.embedding_base_url,
        model=settings.embedding_model,
    )


def _tags_to_text(tags: list[str]) -> str:
    return ",".join(tags or [])


def _tags_from_text(value: str) -> list[str]:
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def _to_langchain_document(document: dict) -> Document:
    return Document(
        page_content=document["content"],
        metadata={
            "id": document["id"],
            "title": document["title"],
            "file": document["file"],
            "chunkIndex": int(document["chunkIndex"]),
            "topic": document.get("topic", ""),
            "level": document.get("level", ""),
            # Chroma 的 metadata 只稳定支持基础类型，所以 tags 用字符串保存。
            "tags": _tags_to_text(document.get("tags", [])),
        },
    )


def rebuild_vector_store() -> dict:
    Chroma = _import_chroma()
    documents = [_to_langchain_document(document) for document in load_knowledge_chunks()]

    if settings.vector_store_dir.exists():
        shutil.rmtree(settings.vector_store_dir)

    settings.vector_store_dir.mkdir(parents=True, exist_ok=True)

    if not documents:
        return {"documentCount": 0, "indexPath": str(settings.vector_store_dir)}

    Chroma.from_documents(
        documents=documents,
        embedding=_create_embedding_model(),
        collection_name=COLLECTION_NAME,
        persist_directory=str(settings.vector_store_dir),
    )

    return {
        "documentCount": len(documents),
        "indexPath": str(settings.vector_store_dir),
        "embeddingModel": settings.embedding_model,
    }


def search_vector_store(question: str, top_k: int | None = None, min_score: float | None = None) -> list[dict]:
    Chroma = _import_chroma()

    if not question.strip():
        return []

    if not settings.vector_store_dir.exists() or not any(settings.vector_store_dir.iterdir()):
        rebuild_vector_store()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_create_embedding_model(),
        persist_directory=str(settings.vector_store_dir),
    )

    results = vector_store.similarity_search_with_relevance_scores(
        question,
        k=top_k or settings.rag_top_k,
    )
    score_threshold = settings.rag_min_score if min_score is None else min_score
    documents: list[dict] = []

    for document, score in results:
        normalized_score = max(0, min(1, float(score)))

        if normalized_score < score_threshold:
            continue

        metadata = document.metadata
        documents.append(
            {
                "title": metadata.get("title", ""),
                "file": metadata.get("file", ""),
                "chunkIndex": int(metadata.get("chunkIndex", 0)),
                "content": document.page_content,
                "topic": metadata.get("topic", ""),
                "level": metadata.get("level", ""),
                "tags": _tags_from_text(metadata.get("tags", "")),
                "score": round(normalized_score, 4),
            }
        )

    return documents
