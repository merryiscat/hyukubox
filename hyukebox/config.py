"""Configuration management using pydantic-settings."""

import sys
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings can be overridden via .env file or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Spotify API
    spotify_client_id: str = ""
    spotify_client_secret: str = ""

    # Last.fm API
    lastfm_api_key: str = ""

    # Anthropic API (Claude)
    anthropic_api_key: str = ""

    # YouTube API
    youtube_credentials_path: Path = Path("./config/youtube_credentials.json")
    youtube_token_path: Path = Path("./config/youtube_token.pickle")

    # Configuration
    cache_dir: Path = Path("./cache")
    cache_ttl: int = 86400  # 24 hours
    log_level: str = "INFO"
    max_playlist_size: int = 20
    default_language_context: str = "korean"

    # Rate Limiting (requests per minute)
    spotify_rate_limit: int = 180
    lastfm_rate_limit: int = 300

    # LLM Settings
    llm_model: str = "claude-opus-4-5-20251101"
    llm_max_tokens: int = 2000
    llm_temperature: float = 0.7

    def validate_required_keys(self) -> None:
        """Validate that required API keys are set.

        Raises:
            ValueError: If required keys are missing
        """
        missing = []

        if not self.spotify_client_id:
            missing.append("SPOTIFY_CLIENT_ID")
        if not self.spotify_client_secret:
            missing.append("SPOTIFY_CLIENT_SECRET")
        if not self.lastfm_api_key:
            missing.append("LASTFM_API_KEY")
        if not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")

        if missing:
            print(
                f"⚠️  Missing required API keys: {', '.join(missing)}\n"
                f"Please set them in .env file or environment variables.",
                file=sys.stderr
            )
            raise ValueError(f"Missing required API keys: {missing}")


# Global settings instance
settings = Settings()
