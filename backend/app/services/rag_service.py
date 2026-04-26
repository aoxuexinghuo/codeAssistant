from .llm_service import generate_reply, stream_reply
from .retriever_service import rebuild_index, retrieve_documents


def rebuild_rag_index() -> dict:
    return rebuild_index()


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


def _build_rag_prompts(question: str) -> tuple[str, str, list[dict]]:
    documents = retrieve_documents(question)
    _log_retrieval(question, documents)
    context = _build_context(documents)
    system_prompt = (
        "你是一个编程教学助手。"
        "请优先依据给定资料片段回答。"
        "如果资料中没有直接依据，先说明资料库没有找到直接依据，再给出简短通用解释。"
        "回答控制在 150 字以内。"
        "不要编造资料来源。"
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


def generate_rag_reply(question: str) -> dict:
    system_prompt, user_prompt, documents = _build_rag_prompts(question)
    reply = generate_reply(system_prompt=system_prompt, user_prompt=user_prompt)
    return {"reply": reply, "sources": _sources_from_documents(documents)}


def stream_rag_reply(question: str):
    system_prompt, user_prompt, documents = _build_rag_prompts(question)
    return {
        "sources": _sources_from_documents(documents),
        "chunks": stream_reply(system_prompt=system_prompt, user_prompt=user_prompt),
    }
