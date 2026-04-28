from .llm_service import generate_reply, stream_reply
from .profile_service import get_profile_for_prompt
from .retriever_service import rebuild_index, retrieve_documents


def rebuild_rag_index() -> dict:
    keyword_result = rebuild_index()

    if keyword_result and keyword_result.get("documentCount", 0) == 0:
        return {"keyword": keyword_result}

    try:
        from .vector_store_service import rebuild_vector_store

        vector_result = rebuild_vector_store()
        return {"keyword": keyword_result, "vector": vector_result}
    except Exception as error:
        print("[rag] vector index rebuild skipped", {"detail": str(error)})
        return {
            "keyword": keyword_result,
            "vector": {
                "enabled": False,
                "reason": str(error),
            },
        }


def search_rag_documents(question: str, user_id: int | None = None) -> list[dict]:
    return retrieve_documents(question, user_id=user_id)


def _build_context(documents: list[dict]) -> str:
    if not documents:
        return "资料库中没有检索到相关片段。"

    parts = []
    for index, document in enumerate(documents, start=1):
        parts.append(
            "\n".join(
                [
                    f"[资料 {index}] {document['title']} ({document['file']})",
                    document["content"],
                ]
            )
        )

    return "\n\n".join(parts)


def _log_retrieval(question: str, documents: list[dict]) -> None:
    if not documents:
        print("[rag] no hit", {"question": question})
        return

    for document in documents:
        print(
            "[rag] hit",
            {
                "question": question,
                "file": document["file"],
                "title": document["title"],
                "chunkIndex": document["chunkIndex"],
                "score": document["score"],
            },
        )


def _sources_from_documents(documents: list[dict]) -> list[dict]:
    return [
        {
            "title": document["title"],
            "file": document["file"],
            "chunkIndex": document["chunkIndex"],
            "score": document["score"],
        }
        for document in documents
    ]


def _build_rag_prompts(question: str, user_id: int | None = None) -> tuple[str, str, list[dict]]:
    documents = retrieve_documents(question, user_id=user_id)
    _log_retrieval(question, documents)
    context = _build_context(documents)
    profile = get_profile_for_prompt(user_id=user_id)
    system_prompt = (
        "你是一个编程教学助手。"
        "请优先依据给定资料片段回答。"
        "如果资料中没有直接依据，先说明资料库没有找到直接依据，再给出简短通用解释。"
        "回答控制在 150 字以内。"
        "不要编造资料来源。"
        f"用户水平是{profile.get('level')}，学习方向是{profile.get('focus')}，回答偏好是{profile.get('answerStyle')}。"
    )
    user_prompt = "\n".join(
        [
            "资料片段：",
            context,
            "",
            f"用户问题：{question}",
            "",
            "请给出简洁回答。",
        ]
    )
    return system_prompt, user_prompt, documents


def generate_rag_reply(question: str, user_id: int | None = None) -> dict:
    system_prompt, user_prompt, documents = _build_rag_prompts(question, user_id=user_id)
    reply = generate_reply(system_prompt=system_prompt, user_prompt=user_prompt)
    return {"reply": reply, "sources": _sources_from_documents(documents)}


def stream_rag_reply(question: str, user_id: int | None = None):
    system_prompt, user_prompt, documents = _build_rag_prompts(question, user_id=user_id)
    return {
        "sources": _sources_from_documents(documents),
        "chunks": stream_reply(system_prompt=system_prompt, user_prompt=user_prompt),
    }
