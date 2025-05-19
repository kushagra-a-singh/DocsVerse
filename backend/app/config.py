import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class OCRSettings(BaseSettings):
    enabled: bool = bool(os.getenv("OCR_ENABLED", "False").lower() == "true")
    language: str = os.getenv("OCR_LANGUAGE", "eng")


class FileStorageSettings(BaseSettings):
    upload_dir: str = os.getenv("UPLOAD_DIR", os.path.abspath("data/uploads"))
    processed_dir: str = os.getenv("PROCESSED_DIR", os.path.abspath("data/processed"))


class OpenAISettings(BaseSettings):
    api_key: str = os.getenv("OPENAI_API_KEY", "")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")


class VectorDBSettings(BaseSettings):
    chunk_size: int = int(os.getenv("VECTOR_DB_CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("VECTOR_DB_CHUNK_OVERLAP", "200"))
    persist_directory: str = os.getenv("VECTOR_DB_PERSIST_DIR", "data/vectordb")
    collection_name: str = os.getenv("VECTOR_DB_COLLECTION", "documents")
    embedding_function: str = os.getenv(
        "VECTOR_DB_EMBEDDING_FUNCTION", "sentence_transformer"
    )
    model_name: str = os.getenv("VECTOR_DB_MODEL_NAME", "all-MiniLM-L6-v2")
    search_limit: int = int(os.getenv("VECTOR_DB_SEARCH_LIMIT", "20"))


class LLMSettings(BaseSettings):
    provider: str = os.getenv("LLM_PROVIDER", "google")
    hf_model: str = os.getenv("HF_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "512"))
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))


class Settings(BaseSettings):

    APP_NAME: str = "Document Research & Theme Identification Chatbot"
    APP_VERSION: str = "1.0.0"

    # api keys, use any llm you like
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.abspath('data/app.db')}"
    )
    DATABASE_ECHO: bool = bool(os.getenv("DATABASE_ECHO", "False"))

    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "data/chroma")

    file_storage: FileStorageSettings = FileStorageSettings()

    ocr: OCRSettings = OCRSettings()

    model_cache_dir: str = os.getenv("MODEL_CACHE_DIR", "./models")
    llm: LLMSettings = LLMSettings()

    vector_db: VectorDBSettings = VectorDBSettings()

    google_api_key: str

    model_config = SettingsConfigDict(
        extra="allow", env_file=".env", env_file_encoding="utf-8"
    )

    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10")) * 1024 * 1024


settings = Settings()
