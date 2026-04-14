"""
Language Adapter — Loads and resolves language-specific configuration.

This is the only module that reads locale JSON files. All other engine
modules receive pre-resolved config dicts, keeping them language-agnostic.
"""
import json
import re
from pathlib import Path
from typing import Any

from app.config import settings


class LanguageAdapter:
    """
    Loads a locale config and provides helper methods for
    token resolution, digit mapping, and number-to-word conversion.
    """

    def __init__(self, locale: str):
        self.locale = locale
        self.config = self._load_config(locale)
        self._digit_map: dict[str, str] = self.config.get("digit_map", {})
        self._reverse_digit_map: dict[str, str] = {v: k for k, v in self._digit_map.items()}
        self._number_words: dict[str, str] = self.config.get("number_words", {})

    # ------------------------------------------------------------------
    # Config loading
    # ------------------------------------------------------------------

    @staticmethod
    def _load_config(locale: str) -> dict:
        config_path = settings.CONFIGS_DIR / f"{locale}.json"
        if not config_path.exists():
            raise FileNotFoundError(
                f"Language config not found: {config_path}. "
                f"Available configs: {[p.stem for p in settings.CONFIGS_DIR.glob('*.json')]}"
            )
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------------------------
    # Category access
    # ------------------------------------------------------------------

    def get_category_config(self, category: str) -> dict:
        """Return config dict for the given category, or raise KeyError."""
        categories = self.config.get("categories", {})
        if category not in categories:
            raise KeyError(
                f"Category '{category}' not found for locale '{self.locale}'. "
                f"Available: {list(categories.keys())}"
            )
        return categories[category]

    def get_supported_categories(self) -> list[str]:
        return list(self.config.get("categories", {}).keys())

    # ------------------------------------------------------------------
    # Token resolution (used by RuleGenerator)
    # ------------------------------------------------------------------

    def resolve_token(self, token: str, category_config: dict) -> str:
        """
        Resolve a {token} placeholder into its regex character class.

        Handles:
          {digits}          → [0-9०-९]
          {native_digit_range} → ०-९
          {symbols}         → [₹\\$]  (from category symbols list)
          {suffixes}        → (वां|वीं|वें|...)
          {separator_chars} → /\\-\\.
          {periods}         → (AM|PM|सुबह|...)
          {unit_names}      → (kg|km|किलोग्राम|...)
        """
        native_range = self.config.get("digit_range_native", "")

        if token == "native_digit_range":
            return native_range
        elif token == "digits":
            return f"[0-9{native_range}]"
        elif token == "symbol_chars":
            symbols = category_config.get("symbols", [])
            return "".join(re.escape(s) for s in symbols)
        elif token == "symbol_alternation":
            symbols = category_config.get("symbols", [])
            return "|".join(re.escape(s) for s in symbols)
        elif token == "suffix_alternation":
            suffixes = category_config.get("suffixes", [])
            return "|".join(re.escape(s) for s in suffixes)
        elif token == "separator_chars":
            separators = category_config.get("separators", [])
            return "".join(re.escape(s) for s in separators)
        elif token == "period_alternation":
            markers = category_config.get("period_markers", [])
            return "|".join(re.escape(s) for s in markers)
        elif token == "unit_alternation":
            unit_map = category_config.get("unit_map", {})
            # Sort by length (longest first) so longer units match before shorter
            units = sorted(unit_map.keys(), key=len, reverse=True)
            return "|".join(re.escape(u) for u in units)
        else:
            return token

    # ------------------------------------------------------------------
    # Digit mapping
    # ------------------------------------------------------------------

    def native_to_ascii(self, text: str) -> str:
        """Convert native digits to ASCII: ५०० → 500"""
        result = []
        for ch in text:
            result.append(self._digit_map.get(ch, ch))
        return "".join(result)

    def ascii_to_native(self, text: str) -> str:
        """Convert ASCII digits to native: 500 → ५००"""
        result = []
        for ch in text:
            result.append(self._reverse_digit_map.get(ch, ch))
        return "".join(result)

    # ------------------------------------------------------------------
    # Number to words (spoken form)
    # ------------------------------------------------------------------

    def number_to_words(self, number: int) -> str:
        """
        Convert an integer to its spoken word form.
        Uses the Indian numbering system (lakh / crore).

        Example (Hindi): 1523 → "एक हज़ार पाँच सौ तेईस"
        """
        if number < 0:
            return self._number_words.get("minus", "माइनस") + " " + self.number_to_words(-number)

        if number == 0:
            return self._number_words.get("0", "शून्य")

        # Check direct lookup first (0-99 are all mapped)
        if str(number) in self._number_words:
            return self._number_words[str(number)]

        parts = []
        w = self._number_words

        # Indian system: crore (10^7), lakh (10^5), thousand, hundred
        if number >= 10_000_000:
            crore = number // 10_000_000
            parts.append(self.number_to_words(crore) + " " + w.get("10000000", "करोड़"))
            number %= 10_000_000

        if number >= 100_000:
            lakh = number // 100_000
            parts.append(self.number_to_words(lakh) + " " + w.get("100000", "लाख"))
            number %= 100_000

        if number >= 1_000:
            thousand = number // 1_000
            parts.append(self.number_to_words(thousand) + " " + w.get("1000", "हज़ार"))
            number %= 1_000

        if number >= 100:
            hundred = number // 100
            parts.append(self.number_to_words(hundred) + " " + w.get("100", "सौ"))
            number %= 100

        if number > 0:
            if str(number) in w:
                parts.append(w[str(number)])
            else:
                # Fallback: digit-by-digit
                for ch in str(number):
                    parts.append(w.get(ch, ch))

        return " ".join(parts)

    # ------------------------------------------------------------------
    # Full config access
    # ------------------------------------------------------------------

    @property
    def language_name(self) -> str:
        return self.config.get("language", self.locale)

    @property
    def script(self) -> str:
        return self.config.get("script", "Unknown")

    def get_info(self) -> dict[str, Any]:
        return {
            "locale": self.locale,
            "language": self.language_name,
            "script": self.script,
            "categories": self.get_supported_categories(),
        }
