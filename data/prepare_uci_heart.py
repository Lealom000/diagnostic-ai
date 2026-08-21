"""Download and normalize the public UCI Heart Disease dataset.

The script creates a local CSV snapshot for offline evaluation. It does not
upload data anywhere and it does not contain credentials.
"""
from __future__ import annotations

import csv
import io
import urllib.request
from pathlib import Path

DATASET_URL = "https://archive.ics.uci.edu/static/public/45/heart+disease.zip"
OUT_DIR = Path(__file__).resolve().parent / "generated"
OUT_FILE = OUT_DIR / "uci_heart_processed.csv"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DATASET_URL, timeout=30) as response:
        payload = response.read()

    import zipfile

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        target = "processed.cleveland.data"
        if target not in zf.namelist():
            raise RuntimeError(f"Expected {target} in UCI archive")
        raw = zf.read(target).decode("utf-8", errors="replace")

    rows = [line.strip().split(",") for line in raw.splitlines() if line.strip()]
    columns = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
    ]

    with OUT_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_FILE}")


if __name__ == "__main__":
    main()
