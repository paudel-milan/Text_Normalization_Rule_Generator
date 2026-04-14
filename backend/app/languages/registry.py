"""
Language Registry — Auto-discovers available language configs.

Adding a new language = dropping a JSON file in configs/.
No code changes required.
"""
from pathlib import Path
from typing import Any

from app.config import settings
from app.languages.adapter import LanguageAdapter


class LanguageRegistry:
    """
    Singleton-pattern registry that scans the configs directory
    and caches LanguageAdapter instances.
    """

    _instance = None
    _adapters: dict[str, LanguageAdapter] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._adapters = {}
            cls._instance._scan()
        return cls._instance

    def _scan(self):
        """Discover all JSON configs in the configs directory."""
        configs_dir = settings.CONFIGS_DIR
        if not configs_dir.exists():
            return
        for config_file in configs_dir.glob("*.json"):
            locale = config_file.stem
            try:
                self._adapters[locale] = LanguageAdapter(locale)
            except Exception as e:
                print(f"[Registry] Warning: Failed to load {locale}: {e}")

    def reload(self):
        """Re-scan configs directory (e.g. after adding a new language)."""
        self._adapters.clear()
        self._scan()

    def get_adapter(self, locale: str) -> LanguageAdapter:
        """Get adapter for a locale, loading on-demand if needed."""
        if locale not in self._adapters:
            # Try loading — will raise FileNotFoundError if not found
            self._adapters[locale] = LanguageAdapter(locale)
        return self._adapters[locale]

    def get_available_languages(self) -> list[dict[str, Any]]:
        """Return info for all discovered languages."""
        return [adapter.get_info() for adapter in self._adapters.values()]

    def get_available_locales(self) -> list[str]:
        """Return list of locale codes."""
        return list(self._adapters.keys())

    def is_supported(self, locale: str) -> bool:
        return locale in self._adapters


# Module-level convenience instance
registry = LanguageRegistry()
