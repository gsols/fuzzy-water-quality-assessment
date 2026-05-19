"""
Purpose: Plot all configured membership functions for inputs and output.
Author: <author>
Date: <date>
"""

import os

# Use a writable cache path so Matplotlib does not warn on locked-down systems.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/water_quality_fuzzy_matplotlib")

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

try:
    from .fuzzy_config import FUZZY_CONFIG
    from .fuzzy_engine import OUTPUT_KEY, get_display_set_name, get_fuzzy_variables
except ImportError:
    from fuzzy_config import FUZZY_CONFIG
    from fuzzy_engine import OUTPUT_KEY, get_display_set_name, get_fuzzy_variables


PLOT_ORDER = [
    "dissolved_oxygen",
    "ph",
    "turbidity",
    "nutrients",
    "temperature",
    "tds",
    OUTPUT_KEY,
]


def _axis_title(key):
    """Create a clear axis title from the configured label and unit."""
    label = FUZZY_CONFIG[key]["label"]
    unit = FUZZY_CONFIG[key]["unit"]
    return f"{label} ({unit})" if unit else label


def plot_membership_functions(save_dir="membership_plots"):
    """Save one filled membership-function plot for every configured variable."""
    variables, water_quality = get_fuzzy_variables()
    all_variables = {**variables, OUTPUT_KEY: water_quality}
    os.makedirs(save_dir, exist_ok=True)
    saved_paths = []

    for key in PLOT_ORDER:
        variable = all_variables[key]
        plt.figure(figsize=(8, 4.5))

        # Filled curves make the overlaps between neighboring trapmfs visible.
        for set_name in FUZZY_CONFIG[key]["sets"]:
            membership = variable[set_name].mf
            plt.plot(variable.universe, membership, linewidth=2,
                     label=get_display_set_name(set_name))
            plt.fill_between(variable.universe, 0, membership, alpha=0.18)

        plt.title(f"{_axis_title(key)} Membership Functions")
        plt.xlabel(_axis_title(key))
        plt.ylabel("Membership Degree")
        plt.ylim(-0.02, 1.05)
        plt.grid(True, alpha=0.3)
        plt.legend(loc="best")
        plt.tight_layout()

        filename = f"{key}_membership.png"
        path = os.path.join(save_dir, filename)
        plt.savefig(path, dpi=150)
        plt.close()
        saved_paths.append(path)

    return saved_paths


def plot_output_with_score(score, save_path):
    """Save the output membership plot with a vertical line at the score."""
    _variables, water_quality = get_fuzzy_variables()
    key = OUTPUT_KEY
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    plt.figure(figsize=(8, 4.5))
    for set_name in FUZZY_CONFIG[key]["sets"]:
        membership = water_quality[set_name].mf
        plt.plot(water_quality.universe, membership, linewidth=2,
                 label=get_display_set_name(set_name))
        plt.fill_between(water_quality.universe, 0, membership, alpha=0.18)

    plt.axvline(score, color="black", linewidth=2, linestyle="--",
                label=f"Score: {score:.2f}")
    plt.title(f"{_axis_title(key)} Membership Functions")
    plt.xlabel(_axis_title(key))
    plt.ylabel("Membership Degree")
    plt.ylim(-0.02, 1.05)
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


if __name__ == "__main__":
    paths = plot_membership_functions()
    print("Saved membership plots:")
    for path in paths:
        print(f"- {path}")
