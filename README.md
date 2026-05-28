# Fuzzy Water Quality Assessment

This project implements a **Fuzzy Logic-Based Surface Water Quality Assessment System** in Python. It uses a Mamdani Fuzzy Inference System to evaluate surface water bodies such as rivers, lakes, and reservoirs based on six water quality parameters, then produces a single **Water Quality Index (WQI)** from 0 to 100.

The assessment design is based on environmental water quality concerns aligned with **DENR DAO 2016-08** in the Philippines and supported by common international water quality references.

## Features

- Mamdani fuzzy inference system using `scikit-fuzzy`
- Six input water quality parameters with weighted importance
- Trapezoidal membership functions for all input and output fuzzy sets
- Centralized fuzzy configuration in one file
- Rule base covering ideal, polluted, mixed, and stressed water conditions
- Command-line test scenarios with expected labels
- Matplotlib membership function visualizations
- Flask web app with form input, result badge, interpretation, and inline output plot

## Input Parameters

| Parameter                    | Unit  | Weight |
| ---------------------------- | ----- | -----: |
| Dissolved Oxygen (DO)        | mg/L  |    25% |
| pH                           | none  |    20% |
| Turbidity                    | NTU   |    18% |
| Nutrients                    | mg/L  |    15% |
| Water Temperature            | deg C |    12% |
| Total Dissolved Solids (TDS) | mg/L  |    10% |

## Output Labels

The system returns a numeric Water Quality Index and a classification label:

| Score Range | Label      |
| ----------- | ---------- |
| `< 25`      | Poor       |
| `< 45`      | Fair       |
| `< 65`      | Acceptable |
| `< 80`      | Good       |
| `>= 80`     | Excellent  |

## Project Structure

```text
.
├── fuzzy_config.py
├── fuzzy_engine.py
├── visualize.py
├── test_scenarios.py
├── app.py
├── index.html
└── static/
    └── style.css
```

## File Overview

- `fuzzy_config.py` stores all universes, trapezoidal membership ranges, labels, units, and weights in `FUZZY_CONFIG`.
- `fuzzy_engine.py` dynamically builds the fuzzy variables, defines the Mamdani rule base, and exposes `evaluate(...)`.
- `visualize.py` generates membership function plots for all six inputs and the WQI output.
- `test_scenarios.py` runs five required scenarios and prints a pass/fail table.
- `app.py` provides the Flask web interface.
- `index.html` contains the single-page form and result section.
- `static/style.css` styles the web application and result badges.

## Requirements

Use Python 3 with these main packages:

```text
scikit-fuzzy
numpy
matplotlib
flask
```

Depending on the Python environment, `scikit-fuzzy` may also require runtime dependencies such as `scipy` and `networkx`.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install scikit-fuzzy numpy matplotlib flask
```

If your environment reports missing `scipy` or `networkx` when importing `scikit-fuzzy`, install them too:

```bash
pip install scipy networkx
```

## Run the Test Scenarios

From the project root:

```bash
python test_scenarios.py
```

Expected output:

```text
Scenario                   Score        Result      Expected    Status
----------------------------------------------------------------------
Pristine Spring                    89.79     Excellent     Excellent      PASS
Clear Mountain Stream              80.35     Excellent     Excellent      PASS
Ideal River                        89.37     Excellent     Excellent      PASS
Healthy River                      70.58          Good          Good      PASS
Cool Clear Stream                  70.82          Good          Good      PASS
Low-Impact Lake                    70.58          Good          Good      PASS
Urban Stream                       52.50    Acceptable    Acceptable      PASS
Moderately Loaded River            52.50    Acceptable    Acceptable      PASS
Suburban Canal                     56.07    Acceptable    Acceptable      PASS
Agricultural Drain                 32.50          Fair          Fair      PASS
Warm Low-DO River                  32.50          Fair          Fair      PASS
Turbid Runoff                      30.85          Fair          Fair      PASS
Anoxic Pond                        20.22          Poor          Poor      PASS
Severely Polluted Lake             20.22          Poor          Poor      PASS
Nutrient Overloaded                21.61          Poor          Poor      PASS
```

Scores may vary slightly if membership functions or rules are adjusted.

## Generate Membership Plots

Run:

```bash
python visualize.py
```

This creates a `membership_plots/` directory with one plot for each input parameter, one plot for the output WQI variable, and one combined overview plot named `all_membership_functions.png`.

## Run the Web App

Start the Flask development server:

```bash
flask --app app run
```

Or run the module directly:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The web app provides:

- Six numeric input fields with valid range hints
- An **Assess Water Quality** submit button
- Numeric WQI score
- Large quality label
- Color-coded badge
- One-sentence interpretation
- Output membership plot showing where the computed score falls

## Programmatic Usage

Use the engine directly from Python:

```python
from fuzzy_engine import evaluate

score, label = evaluate(
    do=9.5,
    ph=7.2,
    turbidity=2.0,
    nutrients=2.0,
    temperature=24.0,
    tds=120.0,
)

print(score, label)
```

## Configuration Notes

All fuzzy ranges are stored in `fuzzy_config.py`. No membership ranges should be hardcoded in the engine, visualizer, tests, or web app.

Each parameter entry contains:

- `label`
- `unit`
- `universe`
- `weight`
- `sets`

Every fuzzy set uses a trapezoidal membership function represented as:

```python
[a, b, c, d]
```

Where membership rises from `a` to `b`, remains fully active from `b` to `c`, and falls from `c` to `d`.

## Rule Base Coverage

The rule base includes cases for:

- Best case water conditions
- Critical low dissolved oxygen
- Excessive nutrients
- Mixed moderate water conditions
- Temperature stress with low oxygen
- High turbidity with high nutrients
- Slightly off but mostly clean water
- Acidic pH with low oxygen
- Excellent oxygen compensating for slightly cloudy water
- High TDS with otherwise moderate conditions
- Cool temperature with high DO and clear water

## Notes

This system is intended for educational and decision-support use. It should not replace laboratory analysis, official regulatory classification, or professional environmental assessment.
