from functools import cached_property
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LLM-Backend"
    PROJECT_NAME: str = "LLM-Feedback-Assistant"
    HF_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    SUPABASE_URL: str
    SUPABASE_KEY: str
    MEMORY_WINDOW: int = 5  # number of turns to remember

    # provider keys
    llm_provider: str | None = Field(default=None, env="LLM_PROVIDER")
    OPENAI_API_KEY: str | None = Field(default=None, env="OPENAI_API_KEY")
    GEMINI_API_KEY: str | None = Field(default=None, env="GEMINI_API_KEY")
    HF_API_KEY: str | None = Field(default=None, env="HF_API_KEY")
    HF_MODEL_ID: str = Field(default="google/flan-t5-large", env="HF_MODEL_ID")

    @cached_property
    def resolved_provider(self) -> str:
        if self.llm_provider:
            return self.llm_provider.lower()
        if self.OPENAI_API_KEY:
            return "openai"
        if self.GEMINI_API_KEY:
            return "gemini"
        return "huggingface"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
