from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    target_url: str = "http://www.ff.ukim.edu.mk/"
    search_phrase: str = "фармацевтска ботаника"
    baseline_count: int = 0
    poll_interval_seconds: int = 60
    dry_run: bool = False
    request_timeout: float = 20


settings = Settings()
