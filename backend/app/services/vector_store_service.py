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
        raise ValueError("缺少 EMBEDDING_API_KEY 环境变量")
    if not settings.embedding_base_url:
        raise ValueError("缺少 EMBEDDING_BASE_URL 环境变量")
    if not settings.embedding_model:
        raise ValueError("缺少 EMBEDDING_MODEL 环境变量")

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
            "scope": document.get("scope", "system"),
            "userId": int(document.get("userId", 0)),
            # Chroma 的 metadata 只稳定支持基础类型，所以 tags 用字符串保存。
            "tags": _tags_to_text(document.get("tags", [])),
        },
    )


def rebuild_vector_store() -> dict:
    Chroma = _import_chroma()
    documents = [_to_langchain_document(document) for document in load_knowledge_chunks(include_all_users=True)]

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

    results = _similarity_search(vector_store=vector_store, question=question, top_k=top_k, user_id=None)
    return _format_results(results=results, min_score=min_score, user_id=None, top_k=top_k)


def search_vector_store_for_user(
    question: str,
    top_k: int | None = None,
    min_score: float | None = None,
    user_id: int | None = None,
) -> list[dict]:
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
    results = _similarity_search(vector_store=vector_store, question=question, top_k=top_k, user_id=user_id)
    return _format_results(results=results, min_score=min_score, user_id=user_id, top_k=top_k)


def _visibility_filter(user_id: int | None) -> dict:
    if user_id is None:
        return {"scope": "system"}

    return {"$or": [{"scope": "system"}, {"userId": int(user_id)}]}


def _is_visible(metadata: dict, user_id: int | None) -> bool:
    if metadata.get("scope") == "system":
        return True

    return user_id is not None and int(metadata.get("userId", 0)) == int(user_id)


def _similarity_search(vector_store, question: str, top_k: int | None, user_id: int | None):
    k = top_k or settings.rag_top_k

    try:
        return vector_store.similarity_search_with_relevance_scores(
            question,
            k=k,
            filter=_visibility_filter(user_id),
        )
    except Exception as error:
        # 不同 Chroma 版本对 $or 过滤支持略有差异。过滤失败时扩大召回，
        # 再在本地二次过滤，保证不会把其他用户资料返回给当前用户。
        print("[rag] vector metadata filter fallback", {"detail": str(error)})
        return vector_store.similarity_search_with_relevance_scores(question, k=max(k * 8, 20))


def _format_results(
    results,
    min_score: float | None = None,
    user_id: int | None = None,
    top_k: int | None = None,
) -> list[dict]:
    score_threshold = settings.rag_min_score if min_score is None else min_score
    documents: list[dict] = []

    for document, score in results:
        normalized_score = max(0, min(1, float(score)))
        metadata = document.metadata

        if not _is_visible(metadata, user_id):
            continue

        if normalized_score < score_threshold:
            continue

        documents.append(
            {
                "title": metadata.get("title", ""),
                "file": metadata.get("file", ""),
                "chunkIndex": int(metadata.get("chunkIndex", 0)),
                "content": document.page_content,
                "topic": metadata.get("topic", ""),
                "level": metadata.get("level", ""),
                "tags": _tags_from_text(metadata.get("tags", "")),
                "scope": metadata.get("scope", "system"),
                "userId": int(metadata.get("userId", 0)),
                "score": round(normalized_score, 4),
            }
        )

        if len(documents) >= (top_k or settings.rag_top_k):
            break

    return documents
