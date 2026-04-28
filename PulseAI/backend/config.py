from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "PulseAI API"
    app_env: str = "development"
    database_url: str = "sqlite:///./pulseai.db"
    nvidia_api_key: str | None = None
    nvidia_model: str = "meta/llama-3.1-8b-instruct"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    request_timeout_seconds: int = 20

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


# ✅ SAFE DEBUG (no secrets)
print("ENV PATH:", BASE_DIR / ".env")
print("NVIDIA API KEY PRESENT:", bool(settings.nvidia_api_key))