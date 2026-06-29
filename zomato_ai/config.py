import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Load settings from .env file in the base directory
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_URL: str = Field(default="sqlite:///zomato_restaurants.db")
    GEMINI_API_KEY: str = Field(default="")
    GROQ_API_KEY: str = Field(default="")
    BYPASS_LLM: bool = Field(default=False)

    @property
    def db_path(self) -> Path:
        """Returns the resolved absolute path to the SQLite database file."""
        # Check if URL starts with sqlite:///
        if self.DATABASE_URL.startswith("sqlite:///"):
            relative_path = self.DATABASE_URL.replace("sqlite:///", "")
            return BASE_DIR / relative_path
        return BASE_DIR / "zomato_restaurants.db"

# Global settings instance
settings = Settings()
