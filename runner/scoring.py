"""
Scoring engine for cold-coffee test evaluations.

Scoring rules:
  +1 for each expected_pattern matched
  -2 for each anti_pattern matched
  +3 bonus if the test category is "clarification" and output contains questions
"""

import re

import yaml


def score_output(test: dict, output: str) -> dict:
    expected = test.get("expected_patterns", [])
    anti = test.get("anti_patterns", [])
    category = test.get("category", "")

    expected_hits = []
    expected_misses = []
    for pattern in expected:
        if re.search(pattern, output, re.IGNORECASE | re.MULTILINE):
            expected_hits.append(pattern)
        else:
            expected_misses.append(pattern)

    anti_hits = []
    anti_misses = []
    for pattern in anti:
        if re.search(pattern, output, re.IGNORECASE | re.MULTILINE):
            anti_hits.append(pattern)
        else:
            anti_misses.append(pattern)

    base_score = len(expected_hits) - (2 * len(anti_hits))

    bonus = 0
    if category == "clarification" and "?" in output:
        bonus = 3

    total = base_score + bonus

    max_possible = len(expected) + (3 if category == "clarification" else 0)

    return {
        "test_id": test["id"],
        "name": test["name"],
        "category": category,
        "difficulty": test.get("difficulty", 0),
        "expected_hits": expected_hits,
        "expected_misses": expected_misses,
        "anti_hits": anti_hits,
        "anti_avoided": anti_misses,
        "base_score": base_score,
        "bonus": bonus,
        "total_score": total,
        "max_score": max_possible,
        "pct": round(total / max_possible * 100, 1) if max_possible > 0 else 0,
    }


def format_report(test: dict, result: dict) -> str:
    lines = []
    status = "✅" if result["total_score"] > 0 else "❌"
    lines.append(f"{status} {test['name']} ({test['id']})")
    lines.append(f"   Score: {result['total_score']}/{result['max_score']} ({result['pct']}%)")
    lines.append(f"   Difficulty: {'★' * test.get('difficulty', 0)}{'☆' * (5 - test.get('difficulty', 0))}")

    if result["expected_hits"]:
        lines.append(f"   ✓ Matched: {', '.join(result['expected_hits'])}")
    if result["expected_misses"]:
        lines.append(f"   ✗ Missing: {', '.join(result['expected_misses'])}")
    if result["anti_hits"]:
        lines.append(f"   ⚠ Anti-patterns found: {', '.join(result['anti_hits'])}")
    if result["anti_avoided"]:
        lines.append(f"   ✓ Anti-patterns avoided: {', '.join(result['anti_avoided'])}")
    if result["bonus"]:
        lines.append(f"   🎯 Bonus: +{result['bonus']} (asked clarifying questions)")

    return "\n".join(lines)


def format_yaml_results(results: list[dict]) -> str:
    cleaned = []
    for r in results:
        cleaned.append({
            "test_id": r["test_id"],
            "name": r.get("name", ""),
            "status": r.get("status", "scored"),
            "score": r.get("total_score"),
            "max_score": r.get("max_score"),
            "pct": r.get("pct"),
            "expected_hits": r.get("expected_hits", []),
            "expected_misses": r.get("expected_misses", []),
            "anti_hits": r.get("anti_hits", []),
        })
    return yaml.dump({"results": cleaned}, default_flow_style=False, sort_keys=False)
