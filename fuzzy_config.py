"""
Purpose: Central configuration for all fuzzy membership ranges and weights.
Author: <author>
Date: <date>
"""

# FUZZY_CONFIG is the single source of truth for every universe, trapezoidal
# membership function, and parameter weight used by the assessment system.
FUZZY_CONFIG = {
    "dissolved_oxygen": {
        "label": "Dissolved Oxygen",
        "unit": "mg/L",
        "universe": [0, 14, 0.1],
        "weight": 0.25,
        "sets": {
            "very_low": [0, 0, 1, 2],
            "low": [1, 2, 3, 5],
            "moderate": [4, 5, 6, 7],
            "high": [6, 7, 9, 10],
            "excellent": [8, 10, 14, 14],
        },
    },
    "ph": {
        "label": "pH",
        "unit": "",
        "universe": [0, 14, 0.1],
        "weight": 0.20,
        "sets": {
            "acidic": [0, 0, 5.5, 6.8],
            "slightly_acidic": [6.0, 6.4, 6.8, 7.0],
            "neutral": [6.5, 7.0, 7.0, 7.5],
            "slightly_alkaline": [7.0, 7.5, 7.8, 8.0],
            "alkaline": [7.5, 8.5, 14, 14],
        },
    },
    "turbidity": {
        "label": "Turbidity",
        "unit": "NTU",
        "universe": [0, 100, 0.5],
        "weight": 0.18,
        "sets": {
            "clear": [0, 0, 3, 5],
            "slightly_cloudy": [3, 7, 11, 15],
            "cloudy": [10, 18, 25, 30],
            "highly_turbid": [25, 40, 100, 100],
        },
    },
    "nutrients": {
        "label": "Nutrients",
        "unit": "mg/L",
        "universe": [0, 50, 0.1],
        "weight": 0.15,
        "sets": {
            "low": [0, 0, 2, 5],
            "moderate": [3, 7, 11, 15],
            "high": [12, 20, 26, 30],
            "excessive": [25, 35, 50, 50],
        },
    },
    "temperature": {
        "label": "Water Temperature",
        "unit": "deg C",
        "universe": [0, 40, 0.1],
        "weight": 0.12,
        "sets": {
            "cold": [0, 0, 10, 15],
            "cool": [12, 15, 19, 22],
            "optimal": [20, 23, 26, 28],
            "warm": [26, 29, 31, 33],
            "hot": [30, 33, 40, 40],
        },
    },
    "tds": {
        "label": "Total Dissolved Solids",
        "unit": "mg/L",
        "universe": [0, 1200, 1],
        "weight": 0.10,
        "sets": {
            "fresh": [0, 0, 150, 300],
            "moderate": [200, 350, 450, 600],
            "high": [500, 680, 820, 1000],
            "excessive": [900, 1000, 1200, 1200],
        },
    },
    "water_quality": {
        "label": "Water Quality Index",
        "unit": "",
        "universe": [0, 100, 0.5],
        "weight": 1.0,
        "sets": {
            "poor": [0, 0, 15, 25],
            "fair": [20, 30, 35, 45],
            "acceptable": [40, 50, 55, 65],
            "good": [60, 70, 75, 80],
            "excellent": [75, 85, 100, 100],
        },
    },
}
