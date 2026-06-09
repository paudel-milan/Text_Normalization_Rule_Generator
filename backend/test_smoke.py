"""Comprehensive smoke test for all 10 languages × 6 categories."""
import sys
import json

sys.path.insert(0, ".")

from app.core.category_engine import CategoryEngine
from app.core.validator import Validator
from app.languages.registry import LanguageRegistry

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
expected_locales = {
    "hi_IN", "ne_NP", "ml_IN", "kn_IN", "ta_IN",
    "te_IN", "mr_IN", "gu_IN", "as_IN", "en_IN"
}
found_locales = {l["locale"] for l in langs}

print(f"Expected {len(expected_locales)} languages, found {len(found_locales)}")
for l in sorted(langs, key=lambda x: x["locale"]):
    print(f"  {l['locale']}: {l['language']} ({l['script']}) — {len(l['categories'])} categories")

missing = expected_locales - found_locales
if missing:
    print(f"\n  FAIL: Missing languages: {missing}")
    sys.exit(1)
print("  PASS\n")

# ======================================================================
# Test 2: Generate rules for all language × category combos
# ======================================================================
print("=" * 70)
print("TEST 2: Rule Generation (10 languages × 6 categories = 60 combos)")
print("=" * 70)

categories = ["cardinal", "ordinal", "currency", "date", "time", "units"]
gen_pass = 0
gen_fail = 0

for lang in sorted(langs, key=lambda x: x["locale"]):
    locale = lang["locale"]
    for cat in categories:
        try:
            rules = engine.generate_rules(locale, cat)
            regex_valid = rules["regex"]["valid"]
            dfa_count = rules["dfa"]["state_count"]
            if not regex_valid:
                print(f"  FAIL  {locale}/{cat}: regex invalid — {rules['regex'].get('error')}")
                gen_fail += 1
            else:
                gen_pass += 1
        except Exception as e:
            print(f"  FAIL  {locale}/{cat}: {e}")
            gen_fail += 1

print(f"  Results: {gen_pass} passed, {gen_fail} failed out of {gen_pass + gen_fail}")
if gen_fail > 0:
    print("  SOME RULE GENERATION TESTS FAILED")
else:
    print("  ALL PASS\n")

# ======================================================================
# Test 3: Test case validation for all combos
# ======================================================================
print("=" * 70)
print("TEST 3: Test Case Validation (built-in positive/negative tests)")
print("=" * 70)

val_total_pass = 0
val_total_fail = 0

for lang in sorted(langs, key=lambda x: x["locale"]):
    locale = lang["locale"]
    adapter = LanguageRegistry().get_adapter(locale)
    validator = Validator(adapter)
    results = validator.validate_all()
    lang_pass = results["total_passed"]
    lang_fail = results["total_failed"]
    val_total_pass += lang_pass
    val_total_fail += lang_fail
    status = "PASS" if lang_fail == 0 else "FAIL"
    print(f"  {status}  {locale} ({lang['language']}): {lang_pass} passed, {lang_fail} failed")
    if lang_fail > 0:
        for cat_name, cat_result in results["categories"].items():
            for r in cat_result.get("results", []):
                if not r["passed"]:
                    print(f"         {cat_name}: input='{r['input']}' expected={r['expected']} got={r['actual']}")

print(f"\n  Total: {val_total_pass} passed, {val_total_fail} failed")
if val_total_fail > 0:
    print("  SOME VALIDATION TESTS FAILED")
else:
    print("  ALL PASS\n")

# ======================================================================
# Test 4: Normalization smoke tests (one per language)
# ======================================================================
print("=" * 70)
print("TEST 4: Normalization Smoke Tests")
print("=" * 70)

norm_tests = {
    "hi_IN":  ("currency", "price is ₹500"),
    "ne_NP":  ("cardinal", "number is 42"),
    "ml_IN":  ("cardinal", "number is 100"),
    "kn_IN":  ("currency", "price is ₹250"),
    "ta_IN":  ("cardinal", "number is 75"),
    "te_IN":  ("currency", "price is ₹1000"),
    "mr_IN":  ("cardinal", "number is 55"),
    "gu_IN":  ("currency", "price is ₹300"),
    "as_IN":  ("cardinal", "number is 20"),
    "en_IN":  ("currency", "price is ₹500"),
}

norm_pass = 0
norm_fail = 0

for locale, (cat, text) in sorted(norm_tests.items()):
    try:
        result = engine.normalize_text(locale, cat, text)
        has_matches = len(result["matches"]) > 0
        if has_matches:
            print(f"  PASS  {locale}/{cat}: '{text}' → '{result['normalized']}'")
            norm_pass += 1
        else:
            print(f"  FAIL  {locale}/{cat}: no matches in '{text}'")
            norm_fail += 1
    except Exception as e:
        print(f"  FAIL  {locale}/{cat}: {e}")
        norm_fail += 1

print(f"\n  Results: {norm_pass} passed, {norm_fail} failed")
if norm_fail > 0:
    print("  SOME NORMALIZATION TESTS FAILED")
else:
    print("  ALL PASS\n")

# ======================================================================
# Test 5: Number-to-word conversion sanity check
# ======================================================================
print("=" * 70)
print("TEST 5: Number-to-Word Conversion (sample numbers)")
print("=" * 70)

sample_numbers = [0, 1, 10, 42, 99, 100, 500, 1523]
registry = LanguageRegistry()

for locale in sorted(expected_locales):
    adapter = registry.get_adapter(locale)
    samples = []
    for n in sample_numbers:
        word = adapter.number_to_words(n)
        samples.append(f"{n}={word}")
    print(f"  {locale} ({adapter.language_name}):")
    print(f"    {', '.join(samples)}")

print()

# ======================================================================
# Summary
# ======================================================================
print("=" * 70)
total_fails = gen_fail + val_total_fail + norm_fail
if total_fails == 0:
    print("ALL TESTS PASSED")
else:
    print(f"TESTS COMPLETED WITH {total_fails} FAILURE(S)")
    sys.exit(1)
