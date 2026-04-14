"""
Application-level configuration for the TTS Text Normalization Framework.
"""
import os
from pathlib import Path


class Settings:
    """Immutable application settings."""

    APP_NAME: str = "TTS Text Normalization Rule Engine"
    APP_VERSION: str = "1.0.0"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    CONFIGS_DIR: Path = BASE_DIR / "languages" / "configs"

    # API
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Export
    MAX_EXPORT_SIZE_MB: int = 10

    # Supported category types (canonical names)
    CATEGORY_TYPES: list[str] = [
        "cardinal",
        "ordinal",
        "currency",
        "date",
        "time",
        "units",
    ]


settings = Settings()
