from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "adaptive_diagnostic"

    # Optional OpenAI LLM configuration (paid / cloud)
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # Optional local LLM configuration (e.g. Ollama)
    # Example: ollama_base_url="http://localhost:11434", ollama_model="llama3.1"
    ollama_base_url: str | None = None
    ollama_model: str | None = None


settings = Settings()
