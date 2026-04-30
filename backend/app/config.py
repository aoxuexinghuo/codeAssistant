import os
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
USER_KNOWLEDGE_DIR = BASE_DIR / "user_knowledge"
VECTOR_DIR = BASE_DIR / "vector_store"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
USER_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    port: int = int(os.getenv("PORT", "3000"))
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{(DATA_DIR / 'programming_assistant.db').as_posix()}"
    )
    llm_api_key: str = os.getenv("LLM_API_KEY") or os.getenv("DEEPSEEK_API_KEY", "")
    llm_base_url: str = os.getenv(
        "LLM_BASE_URL", "https://api.deepseek.com"
    )
    llm_model: str = os.getenv("LLM_MODEL", "deepseek-v4-flash")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "1200"))
    knowledge_dir: Path = KNOWLEDGE_DIR
    user_knowledge_dir: Path = USER_KNOWLEDGE_DIR
    rag_index_path: Path = DATA_DIR / "rag_index.json"
    vector_store_dir: Path = VECTOR_DIR
    rag_retriever_type: str = os.getenv("RAG_RETRIEVER_TYPE", "keyword")
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "3"))
    rag_min_score: float = float(os.getenv("RAG_MIN_SCORE", "0.25"))
    rag_chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    rag_chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "80"))
    embedding_api_key: str = os.getenv("EMBEDDING_API_KEY", "")
    embedding_base_url: str = os.getenv("EMBEDDING_BASE_URL", "")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "")


settings = Settings()
