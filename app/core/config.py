from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Project configuration loaded from .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Enterprise RAG Agent", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    knowledge_base_dir: Path = Field(default=Path("data/knowledge_base"), alias="KNOWLEDGE_BASE_DIR")
    upload_dir: Path = Field(default=Path("data/uploads"), alias="UPLOAD_DIR")
    storage_dir: Path = Field(default=Path("storage"), alias="STORAGE_DIR")
    chunk_store_path: Path = Field(default=Path("storage/chunks.json"), alias="CHUNK_STORE_PATH")
    qa_log_path: Path = Field(default=Path("storage/qa_log.jsonl"), alias="QA_LOG_PATH")

    chunk_size: int = Field(default=600, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=80, alias="CHUNK_OVERLAP")
    top_k: int = Field(default=4, alias="TOP_K")

    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", alias="LLM_BASE_URL")
    llm_model_name: str = Field(default="qwen-plus", alias="LLM_MODEL_NAME")
    llm_timeout: int = Field(default=60, alias="LLM_TIMEOUT")

    def ensure_dirs(self) -> None:
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.storage_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    config = Settings()
    config.ensure_dirs()
    return config


settings = get_settings()
