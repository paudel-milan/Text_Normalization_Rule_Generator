"""
Category Engine — Central orchestrator for rule generation.

Given a language and category, produces a complete RuleBundle:
regex pattern, DFA, SSML template, and normalization output.
"""
from typing import Any

from app.languages.adapter import LanguageAdapter
from app.languages.registry import registry
from app.core.rule_generator import RuleGenerator
from app.core.dfa_builder import DfaBuilder
from app.core.ssml_generator import SsmlGenerator
from app.core.normalizer import Normalizer
from app.core.validator import Validator


class CategoryEngine:
    """
    Orchestrates the full rule generation pipeline.

    This is the single entry point used by the API layer.
    All complexity is delegated to the components.
    """

    def __init__(self):
        self.dfa_builder = DfaBuilder()

    def generate_rules(self, locale: str, category: str) -> dict[str, Any]:
        """
        Generate complete rule bundle for a language + category.

        Returns:
          {
            "locale": "hi_IN",
            "language": "Hindi",
            "category": "currency",
            "regex": {
              "pattern": "...",
              "valid": True
            },
            "dfa": {
              "states": [...],
              "transitions": {...},
              ...
            },
            "ssml": {
              "template": "...",
              "example": "..."
            }
          }
        """
        adapter = registry.get_adapter(locale)
        rule_gen = RuleGenerator(adapter)
        ssml_gen = SsmlGenerator(adapter)

        # Generate regex
        pattern = rule_gen.generate(category)
        pattern_info = rule_gen.validate_pattern(pattern)

        # Generate DFA
        dfa = self.dfa_builder.build(pattern)

        # Generate SSML
        ssml = ssml_gen.generate(category)

        return {
            "locale": locale,
            "language": adapter.language_name,
            "category": category,
            "regex": pattern_info,
            "dfa": dfa,
            "ssml": ssml,
        }

    def normalize_text(self, locale: str, category: str, text: str) -> dict[str, Any]:
        """Normalize text using generated rules."""
        adapter = registry.get_adapter(locale)
        normalizer = Normalizer(adapter)
        return normalizer.normalize(text, category)

    def validate_rules(
        self, locale: str, category: str, custom_tests: dict | None = None
    ) -> dict[str, Any]:
        """Validate rules against test cases."""
        adapter = registry.get_adapter(locale)
        validator = Validator(adapter)
        return validator.validate(category, custom_tests)

    def simulate_dfa(
        self, locale: str, category: str, input_string: str
    ) -> dict[str, Any]:
        """Simulate DFA execution for visualization."""
        adapter = registry.get_adapter(locale)
        rule_gen = RuleGenerator(adapter)
        pattern = rule_gen.generate(category)
        dfa = self.dfa_builder.build(pattern)
        simulation = self.dfa_builder.simulate(dfa, input_string)
        simulation["dfa"] = dfa
        return simulation

    def get_languages(self) -> list[dict[str, Any]]:
        """Get all available languages."""
        return registry.get_available_languages()

    def get_categories(self, locale: str) -> list[str]:
        """Get available categories for a language."""
        adapter = registry.get_adapter(locale)
        return adapter.get_supported_categories()
