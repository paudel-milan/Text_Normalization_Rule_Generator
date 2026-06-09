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

# Test 3.1: Konkani
print("=== Test 3.1: Konkani Currency ===")
result_kok = engine.normalize_text("kok_IN", "currency", "किंमत ₹५०० आसा")
print(f"Original: {result_kok['original']}")
print(f"Normalized: {result_kok['normalized']}")
print(f"SSML: {result_kok['ssml_output']}")
print()

# Test 3.2: Tulu
print("=== Test 3.2: Tulu Cardinal ===")
result_tcy = engine.normalize_text("tcy_IN", "cardinal", "೫೦೦ ಜನ")
print(f"Original: {result_tcy['original']}")
print(f"Normalized: {result_tcy['normalized']}")
print(f"SSML: {result_tcy['ssml_output']}")
print()

# Test 3.3: Punjabi
print("=== Test 3.3: Punjabi Time ===")
result_pa = engine.normalize_text("pa_IN", "time", "ਮੀਟਿੰਗ ੫:੩੦ ਵਜੇ ਹੈ")
print(f"Original: {result_pa['original']}")
print(f"Normalized: {result_pa['normalized']}")
print(f"SSML: {result_pa['ssml_output']}")
print()

# Test 4: Languages
print("=== Test 4: Available languages ===")
langs = engine.get_languages()
for l in langs:
    print(f"  {l['locale']}: {l['language']} ({l['script']}) - categories: {l['categories']}")

print()
print("ALL TESTS PASSED")
