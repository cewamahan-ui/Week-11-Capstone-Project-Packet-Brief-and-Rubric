#!/usr/bin/env python3
"""Deterministic fixture generator for the capstone teaching dataset.

    python scripts/make_fixtures.py

Creates:
- fixtures/triage_messages_sample.jsonl   ~300 synthetic triage rows
- fixtures/catalog_listings_sample.jsonl  ~200 synthetic listing rows

Everything is produced from a fixed random seed (seed=42) - there is
no scraping and no network access anywhere in this script. Triage rows
carry only synthetic clinical fields (symptoms, age band, vitals,
labels); they contain no names, phone numbers, emails or national IDs.
Catalog rows are marketplace listings with no clinical fields at all.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

FIXTURES = REPO_ROOT / "fixtures"
TRIAGE_PATH = FIXTURES / "triage_messages_sample.jsonl"
CATALOG_PATH = FIXTURES / "catalog_listings_sample.jsonl"

SEED = 42
TRIAGE_ROWS = 300
CATALOG_ROWS = 200

# --- label vocabulary -------------------------------------------------
URGENCY_LEVELS = ["low", "moderate", "high"]

SYMPTOM_POOL = [
    "headache", "mild_fatigue", "cough", "fever", "chest_pain",
    "routine_checkup", "follow_up", "vomiting", "rash", "dizziness",
    "abdominal_pain", "injury", "minor_cut", "prescription_refill",
    "shortness_of_breath", "infection", "dehydration", "severe_pain",
]

# Symptom -> clinical severity. This table is deliberately kept next to
# the generator: it is the gold labelling view of the dataset.
CLINICAL_SEVERITY = {
    "chest_pain": "high",
    "shortness_of_breath": "high",
    "severe_pain": "high",
    "minor_cut": "high",
    "fever": "moderate",
    "vomiting": "moderate",
    "dehydration": "moderate",
    "infection": "moderate",
    "injury": "moderate",
    "abdominal_pain": "moderate",
    "headache": "moderate",
    "dizziness": "moderate",
    "rash": "moderate",
    "cough": "low",
    "mild_fatigue": "low",
    "routine_checkup": "low",
    "follow_up": "low",
    "prescription_refill": "low",
}

ACUITY_ORDER = ["low", "moderate", "high"]


def worst(*levels: str) -> str:
    return max(levels, key=lambda level: ACUITY_ORDER.index(level))


def escalate(level: str) -> str:
    index = min(ACUITY_ORDER.index(level) + 1, len(ACUITY_ORDER) - 1)
    return ACUITY_ORDER[index]


def department_for(symptoms: list[str], acuity: str) -> str:
    """Gold routing view: independent of the runtime router table."""
    text = " ".join(symptoms)
    if any(token in text for token in ("chest_pain", "minor_cut", "shortness_of_breath")):
        return "emergency_department"
    if acuity == "high":
        return "urgent_care"
    if any(token in text for token in ("routine_checkup", "follow_up", "prescription_refill")):
        return "general_practice"
    if any(token in text for token in ("fever", "vomiting", "infection", "dehydration")):
        return "urgent_care"
    return "primary_care"


def make_triage_rows() -> list[dict]:
    rng = random.Random(SEED)
    rows: list[dict] = []
    for index in range(1, TRIAGE_ROWS + 1):
        age = rng.choice(
            [rng.randint(1, 12), rng.randint(18, 49), rng.randint(50, 72), rng.randint(65, 88)]
        )
        symptoms = rng.sample(SYMPTOM_POOL, k=rng.randint(1, 3))
        urgency_level = rng.choice(URGENCY_LEVELS)
        vitals = {
            "temperature": round(rng.uniform(36.4, 39.8), 1),
            "heart_rate": rng.randint(58, 128),
        }

        clinical = "low"
        for symptom in symptoms:
            clinical = worst(clinical, CLINICAL_SEVERITY.get(symptom, "low"))
        if vitals["temperature"] >= 39.5:
            clinical = worst(clinical, "high")
        elif vitals["temperature"] >= 38.0:
            clinical = worst(clinical, "moderate")
        if vitals["heart_rate"] >= 120 or vitals["heart_rate"] <= 50:
            clinical = worst(clinical, "high")
        if age >= 65 or age <= 2:
            clinical = escalate(clinical)

        expected_urgency = worst(urgency_level, clinical)

        rows.append(
            {
                "id": f"triage-{index:04d}",
                "age": age,
                "symptoms": sorted(symptoms),
                "urgency_level": urgency_level,
                "vitals": vitals,
                "expected_urgency": expected_urgency,
                "expected_department": department_for(symptoms, expected_urgency),
                "source": "synthetic_generator_seed42",
            }
        )
    return rows

RECOMMENDATION_TOKENS = {
    "high": "immediate_attention",
    "moderate": "within_24_hours",
    "low": "routine_follow_up",
}

def finalise_recommendations(rows: list[dict]) -> list[dict]:
    """Attach the gold disposition token for each row's acuity."""
    for row in rows:
        row["expected_recommendation"] = RECOMMENDATION_TOKENS[row["expected_urgency"]]
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
    triage_rows = finalise_recommendations(make_triage_rows())
    catalog_rows = make_catalog_rows()
    write_jsonl(TRIAGE_PATH, triage_rows)
    write_jsonl(CATALOG_PATH, catalog_rows)
    print(f"wrote {len(triage_rows)} rows -> {TRIAGE_PATH.relative_to(REPO_ROOT)}")
    print(f"wrote {len(catalog_rows)} rows -> {CATALOG_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
