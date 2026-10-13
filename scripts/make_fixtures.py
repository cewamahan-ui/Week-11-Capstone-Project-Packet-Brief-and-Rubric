#!/usr/bin/env python3
"""Deterministic fixture generator for the capstone teaching dataset.

    python scripts/make_fixtures.py

Creates:
- fixtures/triage_messages_sample.jsonl   300 synthetic triage rows
- fixtures/catalog_listings_sample.jsonl  200 synthetic listing rows

Everything is produced from a fixed random seed (seed=42) - there is
no scraping and no network access anywhere in this script. Triage rows
carry only synthetic clinical fields (symptoms, age, vitals, labels);
they contain no names, phone numbers, emails or national IDs.
Catalog rows are marketplace listings with no clinical fields at all.

Gold labels (expected_urgency / expected_recommendation /
expected_department) come from src.afyaplus.triage.policy - the same
module the runtime uses. After the label-drift incident
(docs/incidents/2026-10-13-fixture-label-drift.md) the generator no
longer keeps its own copy of the rules.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.afyaplus.triage import policy  # noqa: E402
from src.afyaplus.triage.models import RECOMMENDATION_TOKENS  # noqa: E402

FIXTURES = REPO_ROOT / "fixtures"
TRIAGE_PATH = FIXTURES / "triage_messages_sample.jsonl"
CATALOG_PATH = FIXTURES / "catalog_listings_sample.jsonl"

SEED = 42
TRIAGE_ROWS = 300
CATALOG_ROWS = 200

URGENCY_LEVELS = ["low", "moderate", "high"]

SYMPTOM_POOL = [
    "headache", "mild_fatigue", "cough", "fever", "chest_pain",
    "routine_checkup", "follow_up", "vomiting", "rash", "dizziness",
    "abdominal_pain", "injury", "minor_cut", "prescription_refill",
    "shortness_of_breath", "infection", "dehydration", "severe_pain",
]


def make_triage_rows() -> list[dict]:
    rng = random.Random(SEED)
    rows: list[dict] = []
    for index in range(1, TRIAGE_ROWS + 1):
        age = rng.choice(
            [rng.randint(1, 12), rng.randint(18, 49), rng.randint(50, 72), rng.randint(65, 88)]
        )
        symptoms = sorted(rng.sample(SYMPTOM_POOL, k=rng.randint(1, 3)))
        urgency_level = rng.choice(URGENCY_LEVELS)
        vitals = {
            "temperature": round(rng.uniform(36.4, 39.8), 1),
            "heart_rate": rng.randint(58, 128),
        }

        expected_urgency = policy.compute_acuity(symptoms, age, urgency_level, vitals)
        endpoint, _reason = policy.decide_endpoint(symptoms, expected_urgency)

        rows.append(
            {
                "id": f"triage-{index:04d}",
                "age": age,
                "symptoms": symptoms,
                "urgency_level": urgency_level,
                "vitals": vitals,
                "expected_urgency": expected_urgency,
                "expected_recommendation": RECOMMENDATION_TOKENS[expected_urgency],
                "expected_department": endpoint,
                "source": "synthetic_generator_seed42",
            }
        )
    return rows


ITEMS = [
    ("Examination gloves (pair)", "consumables"),
    ("Surgical masks (box)", "consumables"),
    ("Rapid malaria test kit", "diagnostics"),
    ("Rapid malaria test kit, combo", "diagnostics"),
    ("Digital thermometer", "equipment"),
    ("Automatic blood pressure monitor", "equipment"),
    ("IV giving set", "consumables"),
    ("Amoxicillin 500mg (strip)", "pharmaceuticals"),
    ("Paracetamol 500mg (strip)", "pharmaceuticals"),
    ("Oral rehydration salts (sachet)", "pharmaceuticals"),
    ("Wound dressing set", "consumables"),
    ("Stethoscope", "equipment"),
    ("Wheelchair, folding", "equipment"),
    ("Disposable syringe 5ml", "consumables"),
    ("Glucose test strips (box)", "diagnostics"),
]

SUPPLIERS = ["MedSupply KE", "Lakeside Distributors", "Savannah Medical", "Coast Traders"]
COUNTIES = ["Nairobi", "Kisumu", "Mombasa", "Nakuru", "Uasin Gishu", "Machakos"]


def make_catalog_rows() -> list[dict]:
    rng = random.Random(SEED + 7)
    rows: list[dict] = []
    for index in range(1, CATALOG_ROWS + 1):
        name, category = ITEMS[(index - 1) % len(ITEMS)]
        suffix = f" (pack {index:03d})" if index > len(ITEMS) else ""
        rows.append(
            {
                "item_id": f"cat-{index:04d}",
                "item_name": f"{name}{suffix}",
                "category": category,
                "supplier": rng.choice(SUPPLIERS),
                "county": rng.choice(COUNTIES),
                "unit_price_usd": round(rng.uniform(0.5, 140.0), 2),
                "stock": rng.randint(0, 500),
                "source": "synthetic_generator_seed42",
            }
        )
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    triage_rows = make_triage_rows()
    catalog_rows = make_catalog_rows()
    write_jsonl(TRIAGE_PATH, triage_rows)
    write_jsonl(CATALOG_PATH, catalog_rows)
    print(f"wrote {len(triage_rows)} rows -> {TRIAGE_PATH.relative_to(REPO_ROOT)}")
    print(f"wrote {len(catalog_rows)} rows -> {CATALOG_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
