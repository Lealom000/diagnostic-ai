"""Minimal offline integrity check for the UCI Heart Disease adapter.

This does not claim clinical accuracy. It verifies that a public empirical
record can be represented as observed PatientState facts with provenance.
"""
from __future__ import annotations

import csv
from pathlib import Path

EXPECTED_COLUMNS = {
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
}


def main() -> None:
    path = Path(__file__).resolve().parent / "generated" / "uci_heart_processed.csv"
    if not path.exists():
        raise SystemExit("Run data/prepare_uci_heart.py first.")

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or []) != EXPECTED_COLUMNS:
            raise SystemExit("Unexpected UCI Heart Disease columns")
        rows = list(reader)

    if not rows:
        raise SystemExit("Dataset is empty")

    first = rows[0]
    patient_state = {
        "case_id": "uci-heart-demo-0001",
        "source": "UCI Heart Disease, CC BY 4.0",
        "observed_facts": [
            {"variable": "age", "value": first["age"], "status": "observed"},
            {"variable": "sex", "value": first["sex"], "status": "observed"},
            {"variable": "resting_blood_pressure", "value": first["trestbps"], "status": "observed"},
            {"variable": "cholesterol", "value": first["chol"], "status": "observed"},
            {"variable": "max_heart_rate", "value": first["thalach"], "status": "observed"},
        ],
    }

    print(f"UCI rows: {len(rows)}")
    print(f"PatientState observed_facts: {len(patient_state['observed_facts'])}")
    print("Dataset adapter: PASS")


if __name__ == "__main__":
    main()
