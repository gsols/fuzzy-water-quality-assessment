"""
Purpose: Run water quality assessment scenarios from mockdata.csv and print results.
Author: <author>
Date: <date>
"""

import csv
import os

try:
    from .fuzzy_engine import evaluate
except ImportError:
    from fuzzy_engine import evaluate


CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mockdata.csv")


def load_scenarios(path=CSV_PATH):
    """Read scenarios from the CSV file and return a list of row dicts."""
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def run_scenarios():
    """Evaluate all scenarios from mockdata.csv and print a formatted results table."""
    scenarios = load_scenarios()

    header = (
        f"{'Scenario':<30}"
        f"{'Score':>10}"
        f"{'Result':>14}"
        f"{'Expected':>14}"
        f"{'Status':>10}"
    )
    print(header)
    print("-" * len(header))

    for row in scenarios:
        name = row["name"]
        expected = row["expected"]
        try:
            score, label = evaluate(
                float(row["do"]),
                float(row["ph"]),
                float(row["turbidity"]),
                float(row["nutrients"]),
                float(row["temp"]),
                float(row["tds"]),
            )
            status = "PASS" if label == expected else "FAIL"
            print(
                f"{name:<30}"
                f"{score:>10.2f}"
                f"{label:>14}"
                f"{expected:>14}"
                f"{status:>10}"
            )
        except Exception as exc:
            print(f"{name:<30}{'ERROR':>10}  ({exc})")


if __name__ == "__main__":
    run_scenarios()
