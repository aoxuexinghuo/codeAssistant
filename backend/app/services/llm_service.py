from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..config import settings


def _assert_llm_config() -> None:
    if not settings.llm_api_key:
        raise ValueError("缺少 LLM_API_KEY 或 DASHSCOPE_API_KEY 环境变量")
    if not settings.llm_base_url:
        raise ValueError("缺少 LLM_BASE_URL 环境变量")
    if not settings.llm_model:
        raise ValueError("缺少 LLM_MODEL 环境变量")


def _create_chat_model() -> ChatOpenAI:
    _assert_llm_config()

    # 这里统一走 LangChain 的 ChatOpenAI，并通过 base_url 接阿里云百炼这类
    # OpenAI-compatible 平台。这样后面做 RAG 时，可以继续沿用 LangChain 生态。
    return ChatOpenAI(
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        max_retries=0,
        base_url=settings.llm_base_url,
        streaming=True,
    )


def _build_messages(system_prompt: str, user_prompt: str) -> list:
    return [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]


def _normalize_chunk_text(content) -> str:
    # LangChain 在不同模型下返回的 chunk.content 结构不完全一致：
    # 有时是纯字符串，有时是内容块列表。这里统一压成纯文本。
    if isinstance(content, str):
        return content

    if not isinstance(content, list):
        return ""

    parts: list[str] = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
            continue

        text = getattr(item, "text", None)
        if isinstance(text, str):
            parts.append(text)
            continue

        if isinstance(item, dict) and isinstance(item.get("text"), str):
            parts.append(item["text"])

    return "".join(parts)


def _format_model_error(error: Exception) -> str:
    return (
        "LangChain 模型调用失败: "
        f"baseURL={settings.llm_base_url} "
        f"model={settings.llm_model} "
        f"reason={error}"
    )


def _collect_stream_reply(system_prompt: str, user_prompt: str):
    model = _create_chat_model()
    full_reply = ""

    # 这里直接使用 LangChain 的 stream()。
    # 对只支持流式输出的模型，这条链路比普通 invoke 更稳。
    for chunk in model.stream(_build_messages(system_prompt, user_prompt)):
        text = _normalize_chunk_text(chunk.content)

        if not text:
            continue

        full_reply += text
        yield text

    if not full_reply.strip():
        raise ValueError("模型流式输出为空")


def generate_reply(system_prompt: str, user_prompt: str) -> str:
    try:
        # 即使对外暴露的是“普通回复”接口，内部仍然走流式聚合。
        # 这样流式和非流式接口共用同一套模型调用路径，行为更一致。
        chunks = list(_collect_stream_reply(system_prompt, user_prompt))
        reply = "".join(chunks).strip()
        if not reply:
            raise ValueError("模型流式输出为空")
        return reply
    except Exception as error:
        raise RuntimeError(_format_model_error(error)) from error


def stream_reply(system_prompt: str, user_prompt: str):
    try:
        for chunk in _collect_stream_reply(system_prompt, user_prompt):
            yield chunk
    except Exception as error:
        raise RuntimeError(_format_model_error(error)) from error
