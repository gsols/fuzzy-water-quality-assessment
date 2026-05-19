"""
Purpose: Mamdani fuzzy inference engine for surface water quality assessment.
Author: <author>
Date: <date>
"""

import os

# scikit-fuzzy can import Matplotlib internally; give it a writable cache path.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/water_quality_fuzzy_matplotlib")

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

try:
    from .fuzzy_config import FUZZY_CONFIG
except ImportError:
    from fuzzy_config import FUZZY_CONFIG


# Input keys are separated from the output key so the engine can dynamically
# build antecedents from the same configuration used by plots and the web app.
INPUT_KEYS = [
    "dissolved_oxygen",
    "ph",
    "turbidity",
    "nutrients",
    "temperature",
    "tds",
]
OUTPUT_KEY = "water_quality"


def _make_universe(universe_config):
    """Create an inclusive NumPy universe from [start, stop, step]."""
    start, stop, step = universe_config
    return np.arange(start, stop + step, step)


def _display_set_name(set_name):
    """Convert internal snake_case fuzzy set names into readable labels."""
    return set_name.replace("_", " ").title()


def _build_variable(key, variable_class):
    """Build one scikit-fuzzy Antecedent or Consequent from FUZZY_CONFIG."""
    config = FUZZY_CONFIG[key]
    variable = variable_class(_make_universe(config["universe"]), key)

    # Every membership function is a trapmf and every range comes from config.
    for set_name, trap_points in config["sets"].items():
        variable[set_name] = fuzz.trapmf(variable.universe, trap_points)

    return variable


def _weighted(term, *parameter_keys):
    """Apply the average configured importance weight to a consequent term."""
    average_weight = sum(FUZZY_CONFIG[key]["weight"] for key in parameter_keys)
    average_weight /= len(parameter_keys)
    return term % average_weight


def _build_system():
    """Create all fuzzy variables and define the Mamdani rule base."""
    variables = {
        key: _build_variable(key, ctrl.Antecedent) for key in INPUT_KEYS
    }
    water_quality = _build_variable(OUTPUT_KEY, ctrl.Consequent)

    do = variables["dissolved_oxygen"]
    ph = variables["ph"]
    turbidity = variables["turbidity"]
    nutrients = variables["nutrients"]
    temperature = variables["temperature"]
    tds = variables["tds"]
    wq = water_quality

    # The rules below cover ideal, critical, mixed, and compensating cases.
    # Single-parameter risk rules use configured weights as rule strengths.
    rules = [
        ctrl.Rule(
            do["excellent"]
            & ph["neutral"]
            & turbidity["clear"]
            & nutrients["low"]
            & temperature["optimal"]
            & tds["fresh"],
            wq["excellent"],
        ),
        ctrl.Rule(
            do["excellent"]
            & turbidity["clear"]
            & nutrients["low"]
            & (temperature["cool"] | temperature["optimal"])
            & (ph["neutral"] | ph["slightly_alkaline"]),
            wq["excellent"],
        ),
        ctrl.Rule(
            do["very_low"] | nutrients["excessive"],
            _weighted(wq["poor"], "dissolved_oxygen", "nutrients"),
        ),
        ctrl.Rule(
            do["low"] & ph["acidic"],
            _weighted(wq["poor"], "dissolved_oxygen", "ph"),
        ),
        ctrl.Rule(
            turbidity["highly_turbid"] & nutrients["high"],
            _weighted(wq["poor"], "turbidity", "nutrients"),
        ),
        ctrl.Rule(
            turbidity["highly_turbid"] & nutrients["excessive"],
            _weighted(wq["poor"], "turbidity", "nutrients"),
        ),
        ctrl.Rule(
            temperature["hot"] & do["low"],
            _weighted(wq["fair"], "temperature", "dissolved_oxygen"),
        ),
        ctrl.Rule(
            temperature["warm"] & do["low"],
            _weighted(wq["fair"], "temperature", "dissolved_oxygen"),
        ),
        ctrl.Rule(
            do["moderate"]
            & ph["neutral"]
            & turbidity["slightly_cloudy"]
            & nutrients["moderate"]
            & temperature["optimal"]
            & (tds["fresh"] | tds["moderate"]),
            wq["acceptable"],
        ),
        ctrl.Rule(
            do["moderate"]
            & (ph["slightly_acidic"] | ph["neutral"])
            & turbidity["cloudy"]
            & nutrients["high"],
            wq["fair"],
        ),
        ctrl.Rule(
            do["high"]
            & (ph["neutral"] | ph["slightly_alkaline"])
            & (turbidity["clear"] | turbidity["slightly_cloudy"])
            & (nutrients["low"] | nutrients["moderate"]),
            wq["good"],
        ),
        ctrl.Rule(
            do["excellent"] & turbidity["slightly_cloudy"] & nutrients["low"],
            wq["good"],
        ),
        ctrl.Rule(
            tds["high"]
            & do["moderate"]
            & ph["neutral"]
            & nutrients["moderate"]
            & (temperature["optimal"] | temperature["warm"]),
            _weighted(wq["fair"], "tds"),
        ),
        ctrl.Rule(
            temperature["cool"] & do["high"] & turbidity["clear"],
            wq["good"],
        ),
        ctrl.Rule(
            ph["alkaline"] & (do["low"] | nutrients["high"]),
            _weighted(wq["poor"], "ph", "dissolved_oxygen", "nutrients"),
        ),
        ctrl.Rule(
            tds["excessive"] | turbidity["highly_turbid"],
            _weighted(wq["fair"], "tds", "turbidity"),
        ),
        ctrl.Rule(
            do["high"]
            & ph["neutral"]
            & turbidity["slightly_cloudy"]
            & nutrients["moderate"]
            & temperature["optimal"]
            & tds["moderate"],
            wq["acceptable"],
        ),
        ctrl.Rule(
            do["excellent"]
            & (ph["neutral"] | ph["slightly_alkaline"])
            & turbidity["clear"]
            & nutrients["low"]
            & tds["fresh"],
            wq["excellent"],
        ),
    ]

    return variables, water_quality, ctrl.ControlSystem(rules)


# Build the fuzzy system once at import time so repeated evaluations are quick.
VARIABLES, WATER_QUALITY, CONTROL_SYSTEM = _build_system()


def classify_score(score):
    """Convert a numeric Water Quality Index score into a label."""
    if score < 25:
        return "Poor"
    if score < 45:
        return "Fair"
    if score < 65:
        return "Acceptable"
    if score < 80:
        return "Good"
    return "Excellent"


def evaluate(do, ph, turbidity, nutrients, temperature, tds):
    """Evaluate six water parameters and return (score, quality label)."""
    simulation = ctrl.ControlSystemSimulation(CONTROL_SYSTEM)
    input_values = {
        "dissolved_oxygen": do,
        "ph": ph,
        "turbidity": turbidity,
        "nutrients": nutrients,
        "temperature": temperature,
        "tds": tds,
    }

    # Clamp values to configured universes to keep the web form and CLI robust.
    for key, value in input_values.items():
        start, stop, _step = FUZZY_CONFIG[key]["universe"]
        simulation.input[key] = min(max(float(value), start), stop)

    simulation.compute()
    score = float(simulation.output[OUTPUT_KEY])
    return score, classify_score(score)


def get_fuzzy_variables():
    """Expose built variables for plotting without rebuilding the system."""
    return VARIABLES, WATER_QUALITY


def get_display_set_name(set_name):
    """Expose readable fuzzy set names to other modules."""
    return _display_set_name(set_name)
