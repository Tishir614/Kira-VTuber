from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="KIRA_", extra="ignore")
    host: str = "127.0.0.1"
    port: int = 8765
    llm_base_url: str = "http://127.0.0.1:11434"
    llm_model: str = "qwen3:4b"
    temperature: float = 0.8
    supabase_url: str = ""
    supabase_publishable_key: str = ""

settings = Settings()
