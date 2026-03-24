from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PulseAI API"
    app_env: str = "development"
    database_url: str = "sqlite:///./pulseai.db"
    nvidia_api_key: str | None = None
    nvidia_model: str = "meta/llama-3.1-8b-instruct"
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    request_timeout_seconds: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
