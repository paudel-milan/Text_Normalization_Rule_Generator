"""Quick smoke test for the core engine."""
import sys
import json

sys.path.insert(0, ".")

from app.core.category_engine import CategoryEngine

engine = CategoryEngine()

# Test 1: Generate rules
print("=== Test 1: Generate Currency Rules (Hindi) ===")
rules = engine.generate_rules("hi_IN", "currency")
print(f"Regex: {rules['regex']['pattern']}")
print(f"Valid: {rules['regex']['valid']}")
print(f"DFA states: {rules['dfa']['states']}")
print(f"DFA state count: {rules['dfa']['state_count']}")
print(f"SSML: {rules['ssml']['full_template']}")
print()

# Test 2: Normalize
print("=== Test 2: Normalize text ===")
result = engine.normalize_text("hi_IN", "currency", "price is ₹500")
print(f"Original: {result['original']}")
print(f"Normalized: {result['normalized']}")
print(f"SSML: {result['ssml_output']}")
print(f"Matches: {len(result['matches'])}")
print()

# Test 3: Nepali
print("=== Test 3: Nepali Cardinal ===")
rules_ne = engine.generate_rules("ne_NP", "cardinal")
print(f"Regex: {rules_ne['regex']['pattern']}")
print(f"DFA states: {rules_ne['dfa']['states']}")
print()

# Test 4: Languages
print("=== Test 4: Available languages ===")
langs = engine.get_languages()
for l in langs:
    print(f"  {l['locale']}: {l['language']} ({l['script']}) - categories: {l['categories']}")

print()
print("ALL TESTS PASSED")
