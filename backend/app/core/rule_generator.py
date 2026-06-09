"""
Rule Generator — Config-driven regex pattern builder.

Constructs regex patterns from category config templates by resolving
language-specific tokens. No hardcoded category logic.
"""
import re
from typing import Any

from app.languages.adapter import LanguageAdapter


class RuleGenerator:
    """
    Builds regex patterns from config-driven templates.

    Each category config contains a `pattern_template` with {token}
    placeholders. The generator resolves these tokens using the
    LanguageAdapter, producing a fully-formed regex.
    """

    def __init__(self, adapter: LanguageAdapter):
        self.adapter = adapter

    def generate(self, category: str) -> str:
        """
        Generate a regex pattern for the given category.

        Returns the compiled-ready regex string.
        """
        cat_config = self.adapter.get_category_config(category)
        template = cat_config.get("pattern_template", "")
        tokens = cat_config.get("tokens", {})

        # Resolve all {token} placeholders in the template
        pattern = self._resolve_template(template, tokens, cat_config)
        return pattern

    def _resolve_template(
        self, template: str, tokens: dict[str, str], cat_config: dict
    ) -> str:
        """
        Resolve {token} placeholders in a pattern template.

        Process:
        1. Find all {token} references in the template
        2. For each token, look up its value in the tokens dict
        3. The token value may itself contain {sub_tokens} — resolve recursively
        4. Replace the {token} with the resolved value
        """
        result = template

        # First pass: resolve token definitions from the tokens dict
        for token_name, token_value in tokens.items():
            placeholder = "{" + token_name + "}"
            if placeholder in result:
                resolved_value = self._resolve_value(token_value, cat_config)
                result = result.replace(placeholder, resolved_value)

        # Second pass: resolve any remaining {config_key} references
        result = self._resolve_remaining(result, cat_config)

        return result

    def _resolve_value(self, value: str, cat_config: dict) -> str:
        """Resolve a token value that may contain {sub_tokens}."""
        # Find all {sub_token} references
        sub_tokens = re.findall(r"\{([a-zA-Z_]\w*)\}", value)
        resolved = value
        for sub_token in sub_tokens:
            sub_placeholder = "{" + sub_token + "}"
            sub_value = self.adapter.resolve_token(sub_token, cat_config)
            resolved = resolved.replace(sub_placeholder, sub_value)
        return resolved

    def _resolve_remaining(self, pattern: str, cat_config: dict) -> str:
        """Resolve any remaining {placeholder} references in the pattern."""
        remaining = re.findall(r"\{([a-zA-Z_]\w*)\}", pattern)
        for token in remaining:
            placeholder = "{" + token + "}"
            resolved = self.adapter.resolve_token(token, cat_config)
            pattern = pattern.replace(placeholder, resolved)
        return pattern

    def validate_pattern(self, pattern: str) -> dict[str, Any]:
        """
        Validate that a generated pattern is a valid regex.

        Returns:
          {"valid": True, "pattern": pattern}
          or
          {"valid": False, "error": "error message"}
        """
        try:
            re.compile(pattern, re.UNICODE)
            return {"valid": True, "pattern": pattern}
        except re.error as e:
            return {"valid": False, "error": str(e), "pattern": pattern}
