from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    AGENT_API_KEY: str = "default_api_key"
    monthly_budget_limit: float = 10.00

    class Config:
        env_file = ".env"

settings = Settings()