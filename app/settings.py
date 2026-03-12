from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # define basic application metadata and runtime environment
    app_env: str = "development"
    app_name: str = "Meeting Notes API"
    app_version: str = "0.1.0"

    # define database configuration
    supabase_url: str = ""
    supabase_key: str = ""

    # define llm provider configuration
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # define logging configuration
    log_level: str = "INFO"

    # load environment variables from .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# create a single settings instance for the whole app
settings = Settings()