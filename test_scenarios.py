"""
Purpose: Run required water quality assessment scenarios and print results.
Author: <author>
Date: <date>
"""

try:
    from .fuzzy_engine import evaluate
except ImportError:
    from fuzzy_engine import evaluate


SCENARIOS = [
    ("Clean River", 9.5, 7.2, 2.0, 2.0, 24.0, 120.0, "Excellent"),
    ("Polluted Lake", 2.1, 5.5, 45.0, 28.0, 31.0, 850.0, "Poor"),
    ("Average Stream", 6.5, 7.0, 10.0, 10.0, 26.0, 300.0, "Acceptable"),
    ("Agricultural Runoff", 5.0, 6.8, 20.0, 25.0, 27.0, 400.0, "Fair"),
    ("Pristine Source", 11.0, 7.4, 1.0, 1.0, 20.0, 80.0, "Excellent"),
]


def run_scenarios():
    """Evaluate all required scenarios and print a formatted results table."""
    header = (
        f"{'Scenario':<22}"
        f"{'Score':>10}"
        f"{'Result':>14}"
        f"{'Expected':>14}"
        f"{'Status':>10}"
    )
    print(header)
    print("-" * len(header))

    for name, do, ph, turbidity, nutrients, temp, tds, expected in SCENARIOS:
        score, label = evaluate(do, ph, turbidity, nutrients, temp, tds)
        status = "PASS" if label == expected else "FAIL"
        print(
            f"{name:<22}"
            f"{score:>10.2f}"
            f"{label:>14}"
            f"{expected:>14}"
            f"{status:>10}"
        )


if __name__ == "__main__":
    run_scenarios()
