"""
Normalizer — Applies generated rules to normalize raw text.

Given a text input, locale, and category, this module:
1. Applies the regex pattern to find matches
2. Converts matched text to spoken word form
3. Returns normalized text with SSML markup
"""
import re
from typing import Any

from app.languages.adapter import LanguageAdapter
from app.core.rule_generator import RuleGenerator
from app.core.ssml_generator import SsmlGenerator


class Normalizer:
    """
    Applies TN rules to normalize text.

    Handles all 6 categories with config-driven normalization logic.
    The normalization strategy per category is determined by the
    category name, but the specific mappings/words come from config.
    """

    def __init__(self, adapter: LanguageAdapter):
        self.adapter = adapter
        self.rule_gen = RuleGenerator(adapter)
        self.ssml_gen = SsmlGenerator(adapter)

    def normalize(self, text: str, category: str) -> dict[str, Any]:
        """
        Normalize all occurrences of the category pattern in text.

        Returns:
          {
            "original": "मेरे पास ₹५०० है",
            "normalized": "मेरे पास पाँच सौ रुपये है",
            "ssml_output": "मेरे पास <say-as ...>500</say-as> है",
            "matches": [
              {
                "matched_text": "₹५००",
                "span": [9, 13],
                "normalized_form": "पाँच सौ रुपये",
                "ssml_form": "<say-as...>500</say-as>"
              }
            ],
            "category": "currency",
            "locale": "hi_IN"
          }
        """
        pattern = self.rule_gen.generate(category)
        matches_info = []
        normalized_text = text
        ssml_text = text

        try:
            compiled = re.compile(pattern, re.UNICODE)
        except re.error:
            return {
                "original": text,
                "normalized": text,
                "ssml_output": text,
                "matches": [],
                "category": category,
                "locale": self.adapter.locale,
                "error": f"Invalid regex pattern: {pattern}",
            }

        # Find all matches (process right-to-left to preserve span offsets)
        all_matches = list(compiled.finditer(text))
        for match in reversed(all_matches):
            matched_text = match.group(0)
            span = [match.start(), match.end()]

            # Normalize the matched value based on category
            normalized_form = self._normalize_match(match, category)
            ssml_form = self._ssml_for_match(match, category)

            matches_info.insert(0, {
                "matched_text": matched_text,
                "span": span,
                "groups": [match.group(i) for i in range(match.lastindex + 1)] if match.lastindex else [matched_text],
                "normalized_form": normalized_form,
                "ssml_form": ssml_form,
            })

            # Replace in text (right-to-left preserves positions)
            normalized_text = normalized_text[:match.start()] + normalized_form + normalized_text[match.end():]
            ssml_text = ssml_text[:match.start()] + ssml_form + ssml_text[match.end():]

        return {
            "original": text,
            "normalized": normalized_text,
            "ssml_output": ssml_text,
            "matches": matches_info,
            "category": category,
            "locale": self.adapter.locale,
            "pattern_used": pattern,
        }

    def _normalize_match(self, match: re.Match, category: str) -> str:
        """Convert a regex match to spoken word form based on category."""
        cat_config = self.adapter.get_category_config(category)

        if category == "cardinal":
            return self._normalize_cardinal(match)
        elif category == "ordinal":
            return self._normalize_ordinal(match, cat_config)
        elif category == "currency":
            return self._normalize_currency(match, cat_config)
        elif category == "date":
            return self._normalize_date(match, cat_config)
        elif category == "time":
            return self._normalize_time(match, cat_config)
        elif category == "units":
            return self._normalize_units(match, cat_config)
        else:
            return match.group(0)

    def _normalize_cardinal(self, match: re.Match) -> str:
        """Cardinal: ५०० → पाँच सौ"""
        num_str = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
        ascii_str = self.adapter.native_to_ascii(num_str)
        try:
            number = int(ascii_str)
            return self.adapter.number_to_words(number)
        except ValueError:
            return num_str

    def _normalize_ordinal(self, match: re.Match, cat_config: dict) -> str:
        """Ordinal: ५वां → पाँचवां"""
        num_str = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
        suffix = match.group(2) if match.lastindex and match.lastindex >= 2 else ""
        ascii_str = self.adapter.native_to_ascii(num_str)
        try:
            number = int(ascii_str)
            word = self.adapter.number_to_words(number)
            return f"{word}{suffix}"
        except ValueError:
            return match.group(0)

    def _normalize_currency(self, match: re.Match, cat_config: dict) -> str:
        """Currency: ₹५०० → पाँच सौ रुपये"""
        symbol = match.group(1) if match.lastindex and match.lastindex >= 1 else ""
        amount_str = match.group(2) if match.lastindex and match.lastindex >= 2 else ""
        decimal_str = match.group(3) if match.lastindex and match.lastindex >= 3 else None

        # Get currency name from config
        symbol_names = cat_config.get("symbol_names", {})
        currency_name = symbol_names.get(symbol.strip(), "")

        ascii_amount = self.adapter.native_to_ascii(amount_str)
        try:
            amount = int(ascii_amount)
            amount_words = self.adapter.number_to_words(amount)
        except ValueError:
            amount_words = amount_str

        result = amount_words
        if decimal_str:
            ascii_decimal = self.adapter.native_to_ascii(decimal_str)
            try:
                decimal_num = int(ascii_decimal)
                decimal_words = self.adapter.number_to_words(decimal_num)
                # Get "point" word or use a default
                decimal_connector = self.adapter.config.get("decimal_connector", "दशमलव")
                result += f" {decimal_connector} {decimal_words}"
            except ValueError:
                result += f".{decimal_str}"

        if currency_name:
            result += f" {currency_name}"

        return result

    def _normalize_date(self, match: re.Match, cat_config: dict) -> str:
        """Date: १५/०८/२०२३ → पंद्रह अगस्त दो हज़ार तेईस"""
        day_str = match.group(1) if match.lastindex and match.lastindex >= 1 else ""
        month_str = match.group(2) if match.lastindex and match.lastindex >= 2 else ""
        year_str = match.group(3) if match.lastindex and match.lastindex >= 3 else ""

        month_names = cat_config.get("month_names", [])

        ascii_day = self.adapter.native_to_ascii(day_str)
        ascii_month = self.adapter.native_to_ascii(month_str)
        ascii_year = self.adapter.native_to_ascii(year_str)

        try:
            day_word = self.adapter.number_to_words(int(ascii_day))
        except ValueError:
            day_word = day_str

        try:
            month_idx = int(ascii_month) - 1
            month_word = month_names[month_idx] if 0 <= month_idx < len(month_names) else month_str
        except (ValueError, IndexError):
            month_word = month_str

        try:
            year_word = self.adapter.number_to_words(int(ascii_year))
        except ValueError:
            year_word = year_str

        return f"{day_word} {month_word} {year_word}"

    def _normalize_time(self, match: re.Match, cat_config: dict) -> str:
        """Time: ५:३० → पाँच बजकर तीस मिनट"""
        hour_str = match.group(1) if match.lastindex and match.lastindex >= 1 else ""
        min_str = match.group(2) if match.lastindex and match.lastindex >= 2 else ""
        period = match.group(3) if match.lastindex and match.lastindex >= 3 else ""

        ascii_hour = self.adapter.native_to_ascii(hour_str)
        ascii_min = self.adapter.native_to_ascii(min_str)

        try:
            hour_word = self.adapter.number_to_words(int(ascii_hour))
        except ValueError:
            hour_word = hour_str

        try:
            min_num = int(ascii_min)
            min_word = self.adapter.number_to_words(min_num) if min_num > 0 else ""
        except ValueError:
            min_word = min_str

        time_format = self.adapter.config.get("time_format", {})
        with_minutes_tmpl = time_format.get("with_minutes", "{hour_word} बजकर {min_word} मिनट")
        without_minutes_tmpl = time_format.get("without_minutes", "{hour_word} बजे")

        if min_word:
            result = with_minutes_tmpl.format(hour_word=hour_word, min_word=min_word)
        else:
            result = without_minutes_tmpl.format(hour_word=hour_word)

        if period:
            result += f" {period.strip()}"
        return result

    def _normalize_units(self, match: re.Match, cat_config: dict) -> str:
        """Units: ५ किलोग्राम → पाँच किलोग्राम"""
        num_str = match.group(1) if match.lastindex and match.lastindex >= 1 else ""
        unit_str = match.group(2) if match.lastindex and match.lastindex >= 2 else ""

        unit_map = cat_config.get("unit_map", {})
        spoken_unit = unit_map.get(unit_str, unit_str)

        ascii_num = self.adapter.native_to_ascii(num_str)
        try:
            # Handle decimal numbers
            if "." in ascii_num:
                parts = ascii_num.split(".")
                int_word = self.adapter.number_to_words(int(parts[0]))
                dec_word = self.adapter.number_to_words(int(parts[1]))
                decimal_connector = self.adapter.config.get("decimal_connector", "दशमलव")
                num_word = f"{int_word} {decimal_connector} {dec_word}"
            else:
                num_word = self.adapter.number_to_words(int(ascii_num))
        except ValueError:
            num_word = num_str

        return f"{num_word} {spoken_unit}"

    def _ssml_for_match(self, match: re.Match, category: str) -> str:
        """Generate SSML tag for a matched region."""
        # Use the first captured group as the value, or full match
        value = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
        ascii_value = self.adapter.native_to_ascii(value)
        return self.ssml_gen.render(category, ascii_value)
