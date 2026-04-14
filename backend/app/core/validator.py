"""
Validator — Validates generated rules against test cases.

Runs positive and negative test cases from the category config
to verify that the generated regex pattern behaves correctly.
"""
import re
from typing import Any

from app.languages.adapter import LanguageAdapter
from app.core.rule_generator import RuleGenerator


class Validator:
    """
    Validates a generated regex pattern against test cases
    defined in the category config.
    """

    def __init__(self, adapter: LanguageAdapter):
        self.adapter = adapter
        self.rule_gen = RuleGenerator(adapter)

    def validate(self, category: str, custom_test_cases: dict | None = None) -> dict[str, Any]:
        """
        Validate the generated pattern for a category.

        Uses test cases from config, or custom ones if provided.

        Returns:
          {
            "category": "currency",
            "pattern": "...",
            "total_tests": 10,
            "passed": 8,
            "failed": 2,
            "results": [
              {"input": "₹५००", "expected": "match", "actual": "match", "passed": True},
              ...
            ]
          }
        """
        pattern = self.rule_gen.generate(category)
        cat_config = self.adapter.get_category_config(category)

        # Get test cases
        if custom_test_cases:
            positive = custom_test_cases.get("positive", [])
            negative = custom_test_cases.get("negative", [])
        else:
            test_cases = cat_config.get("test_cases", {})
            positive = test_cases.get("positive", [])
            negative = test_cases.get("negative", [])

        results = []

        try:
            compiled = re.compile(pattern, re.UNICODE)
        except re.error as e:
            return {
                "category": category,
                "pattern": pattern,
                "error": f"Invalid regex: {e}",
                "total_tests": len(positive) + len(negative),
                "passed": 0,
                "failed": len(positive) + len(negative),
                "results": [],
            }

        # Positive tests (should match)
        for test_input in positive:
            match = compiled.search(test_input)
            passed = match is not None
            results.append({
                "input": test_input,
                "expected": "match",
                "actual": "match" if match else "no_match",
                "passed": passed,
                "match_details": {
                    "full_match": match.group(0) if match else None,
                    "groups": list(match.groups()) if match else None,
                } if match else None,
            })

        # Negative tests (should NOT match)
        for test_input in negative:
            match = compiled.fullmatch(test_input)
            passed = match is None
            results.append({
                "input": test_input,
                "expected": "no_match",
                "actual": "no_match" if match is None else "match",
                "passed": passed,
            })

        passed_count = sum(1 for r in results if r["passed"])
        return {
            "category": category,
            "pattern": pattern,
            "total_tests": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "pass_rate": f"{(passed_count / len(results) * 100):.1f}%" if results else "N/A",
            "results": results,
        }

    def validate_all(self) -> dict[str, Any]:
        """Validate all categories for the current language."""
        categories = self.adapter.get_supported_categories()
        all_results = {}
        total_passed = 0
        total_failed = 0

        for category in categories:
            result = self.validate(category)
            all_results[category] = result
            total_passed += result["passed"]
            total_failed += result["failed"]

        return {
            "locale": self.adapter.locale,
            "total_categories": len(categories),
            "total_passed": total_passed,
            "total_failed": total_failed,
            "categories": all_results,
        }
