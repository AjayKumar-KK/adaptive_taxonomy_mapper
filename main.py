#!/usr/bin/env python3
"""
Main runner: Adaptive Taxonomy Mapper

Runs the mapper across the Golden Set and writes results to outputs/results.json

Usage:
  python main.py
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from src.mapper import TaxonomyMapper

ROOT = os.path.dirname(os.path.abspath(__file__))

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def main() -> None:
    taxonomy_path = os.path.join(ROOT, "data", "taxonomy.json")
    testcases_path = os.path.join(ROOT, "data", "test_cases.json")
    out_dir = os.path.join(ROOT, "outputs")
    ensure_dir(out_dir)

    taxonomy: Dict[str, Any] = load_json(taxonomy_path)
    test_cases: List[Dict[str, Any]] = load_json(testcases_path)

    mapper = TaxonomyMapper(taxonomy)

    results = []
    print("\n=== Adaptive Taxonomy Mapper: Results (Readable) ===\n")
    for case in test_cases:
        res = mapper.map(case_id=case["id"], user_tags=case["user_tags"], snippet=case["snippet"])
        results.append({
            "id": res.case_id,
            "user_tags": res.user_tags,
            "snippet": res.snippet,
            "mapped": res.mapped,
            "path": res.path,
            "confidence": round(res.confidence, 4),
            "reasoning": res.reasoning,
            "top_scores": res.scores,
        })

        print(f"Case {res.case_id}")
        print(f"  Tags      : {res.user_tags}")
        print(f"  Snippet   : {res.snippet}")
        print(f"  Mapped    : {res.mapped}")
        if res.path:
            print(f"  Path      : {res.path}")
        print(f"  Confidence: {res.confidence:.2f}")
        if res.scores:
            print(f"  TopScores : {res.scores}")
        print(f"  Reasoning : {res.reasoning}")
        print("-" * 70)

    out_path = os.path.join(out_dir, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved JSON results to: {out_path}\n")
    print("Done.\n")

if __name__ == "__main__":
    main()
