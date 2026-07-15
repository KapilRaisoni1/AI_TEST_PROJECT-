from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "google/gemini-2.5-flash"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()

print("API Key loaded:", bool(settings.OPENROUTER_API_KEY))
print("Model:", settings.OPENROUTER_MODEL)