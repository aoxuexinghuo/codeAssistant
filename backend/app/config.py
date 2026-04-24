import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
VECTOR_DIR = BASE_DIR / "vector_store"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    port: int = int(os.getenv("PORT", "3000"))
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{(DATA_DIR / 'programming_assistant.db').as_posix()}"
    )
    llm_api_key: str = os.getenv("LLM_API_KEY") or os.getenv("DASHSCOPE_API_KEY", "")
    llm_base_url: str = os.getenv(
        "LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    llm_model: str = os.getenv("LLM_MODEL", "qvq-max-2025-03-25")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "1200"))
    knowledge_dir: Path = KNOWLEDGE_DIR
    rag_index_path: Path = DATA_DIR / "rag_index.json"
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "3"))
    rag_chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "80"))


settings = Settings()
