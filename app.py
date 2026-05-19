"""
Purpose: Flask web interface for the fuzzy water quality assessment system.
Author: <author>
Date: <date>
"""

import os

from flask import Flask, render_template, request

try:
    from .fuzzy_config import FUZZY_CONFIG
    from .fuzzy_engine import evaluate
    from .visualize import plot_output_with_score
except ImportError:
    from fuzzy_config import FUZZY_CONFIG
    from fuzzy_engine import evaluate
    from visualize import plot_output_with_score


app = Flask(__name__)


INTERPRETATIONS = {
    "Poor": "Water quality is severely degraded and may require urgent remediation before use.",
    "Fair": "Water quality shows stress and should be monitored or treated for sensitive uses.",
    "Acceptable": "Water quality is generally usable but has moderate limitations.",
    "Good": "Water quality is healthy with only minor concerns.",
    "Excellent": "Water quality is very clean and strongly supports surface water health.",
}


FORM_FIELDS = [
    ("dissolved_oxygen", "do"),
    ("ph", "ph"),
    ("turbidity", "turbidity"),
    ("nutrients", "nutrients"),
    ("temperature", "temperature"),
    ("tds", "tds"),
]


def _field_metadata():
    """Return display metadata and valid ranges for all form inputs."""
    metadata = []
    for config_key, form_name in FORM_FIELDS:
        config = FUZZY_CONFIG[config_key]
        start, stop, _step = config["universe"]
        unit = config["unit"]
        metadata.append(
            {
                "config_key": config_key,
                "name": form_name,
                "label": config["label"],
                "unit": unit,
                "min": start,
                "max": stop,
                "hint": f"Valid range: {start:g} to {stop:g}"
                + (f" {unit}" if unit else ""),
            }
        )
    return metadata


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the form and, after submission, the assessment result."""
    result = None
    values = {}
    error = None

    if request.method == "POST":
        try:
            # Parse all six numeric inputs by their form names.
            for _config_key, form_name in FORM_FIELDS:
                values[form_name] = float(request.form[form_name])

            score, label = evaluate(
                values["do"],
                values["ph"],
                values["turbidity"],
                values["nutrients"],
                values["temperature"],
                values["tds"],
            )

            # Regenerate the output plot so the page shows the score location.
            plot_name = "output_score.png"
            plot_path = os.path.join(app.static_folder, plot_name)
            plot_output_with_score(score, plot_path)

            result = {
                "score": score,
                "label": label,
                "badge_class": label.lower(),
                "interpretation": INTERPRETATIONS[label],
                "plot_url": f"static/{plot_name}",
            }
        except (ValueError, KeyError):
            error = "Please enter valid numeric values for all parameters."

    return render_template(
        "index.html",
        fields=_field_metadata(),
        values=values,
        result=result,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
