"""
Purpose: CustomTkinter desktop interface for the fuzzy water quality assessment system.
Author: <author>
Date: <date>
"""

import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/water_quality_fuzzy_matplotlib")

# Backend must be set before pyplot is imported anywhere in this process.
import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

try:
    from .fuzzy_config import FUZZY_CONFIG
    from .fuzzy_engine import OUTPUT_KEY, evaluate, get_display_set_name, get_fuzzy_variables
except ImportError:
    from fuzzy_config import FUZZY_CONFIG
    from fuzzy_engine import OUTPUT_KEY, evaluate, get_display_set_name, get_fuzzy_variables


# ── Design tokens (mirrors the CSS :root variables) ───────────────────────────
INK      = "#17211b"
MUTED    = "#5d6b63"
LINE     = "#d7e0da"
SURFACE  = "#f7faf8"
PANEL    = "#ffffff"
ACCENT   = "#1f7a67"
ACCENT_H = "#185f50"

BADGE_COLORS = {
    "Poor":       "#c0392b",
    "Fair":       "#e67e22",
    "Acceptable": "#d4a017",
    "Good":       "#2e8b57",
    "Excellent":  "#0b5d3b",
}

BADGE_TEXT = {
    "Acceptable": "#1f1a00",
}

INTERPRETATIONS = {
    "Poor":       "Water quality is severely degraded and may require urgent remediation before use.",
    "Fair":       "Water quality shows stress and should be monitored or treated for sensitive uses.",
    "Acceptable": "Water quality is generally usable but has moderate limitations.",
    "Good":       "Water quality is healthy with only minor concerns.",
    "Excellent":  "Water quality is very clean and strongly supports surface water health.",
}

FORM_FIELDS = [
    ("dissolved_oxygen", "do"),
    ("ph",               "ph"),
    ("turbidity",        "turbidity"),
    ("nutrients",        "nutrients"),
    ("temperature",      "temperature"),
    ("tds",              "tds"),
]

PLOT_ORDER = [
    "dissolved_oxygen", "ph", "turbidity",
    "nutrients", "temperature", "tds", OUTPUT_KEY,
]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
LEFT_W = 300  # fixed left panel width


def _save_figures(fig_output, fig_combined):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fig_output.savefig(os.path.join(OUTPUT_DIR, "output_score.png"), dpi=150)
    fig_combined.savefig(os.path.join(OUTPUT_DIR, "all_membership_functions.png"), dpi=150)


def _build_output_figure(score):
    _vars, water_quality = get_fuzzy_variables()
    fig, ax = plt.subplots(figsize=(7, 4))
    for set_name in FUZZY_CONFIG[OUTPUT_KEY]["sets"]:
        mf = water_quality[set_name].mf
        ax.plot(water_quality.universe, mf, linewidth=2,
                label=get_display_set_name(set_name))
        ax.fill_between(water_quality.universe, 0, mf, alpha=0.18)
    ax.axvline(score, color="black", linewidth=2, linestyle="--",
               label=f"Score: {score:.2f}")
    ax.set_title("Water Quality Index", fontsize=12, fontweight="bold")
    ax.set_xlabel("Water Quality Index")
    ax.set_ylabel("Membership Degree")
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()
    return fig


def _build_combined_figure():
    variables, water_quality = get_fuzzy_variables()
    all_vars = {**variables, OUTPUT_KEY: water_quality}
    fig, axes = plt.subplots(4, 2, figsize=(7, 13))
    flat = axes.flatten()
    for ax, key in zip(flat, PLOT_ORDER):
        cfg = FUZZY_CONFIG[key]
        unit = cfg["unit"]
        title = f"{cfg['label']} ({unit})" if unit else cfg["label"]
        var = all_vars[key]
        for set_name in cfg["sets"]:
            mf = var[set_name].mf
            ax.plot(var.universe, mf, linewidth=1.5,
                    label=get_display_set_name(set_name))
            ax.fill_between(var.universe, 0, mf, alpha=0.16)
        ax.set_title(title, fontsize=9, fontweight="bold")
        ax.set_ylabel("Membership", fontsize=8)
        ax.set_ylim(-0.02, 1.05)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=6)
    for ax in flat[len(PLOT_ORDER):]:
        ax.axis("off")
    fig.suptitle("Fuzzy Membership Functions", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    return fig


def _enable_mousewheel(scrollable_frame):
    """Bind touchpad/mouse-wheel scrolling to a CTkScrollableFrame."""
    canvas = scrollable_frame._parent_canvas

    def _scroll(event):
        if event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")
        else:
            canvas.yview_scroll(1, "units")

    scrollable_frame.bind("<Enter>",
        lambda _: (scrollable_frame.bind_all("<MouseWheel>", _scroll),
                   scrollable_frame.bind_all("<Button-4>", _scroll),
                   scrollable_frame.bind_all("<Button-5>", _scroll)))
    scrollable_frame.bind("<Leave>",
        lambda _: (scrollable_frame.unbind_all("<MouseWheel>"),
                   scrollable_frame.unbind_all("<Button-4>"),
                   scrollable_frame.unbind_all("<Button-5>")))


def _h2(parent, text, row):
    ctk.CTkLabel(
        parent, text=text, text_color=INK, anchor="w",
        font=ctk.CTkFont(family="Arial", size=15, weight="bold"),
    ).grid(row=row, column=0, sticky="w", padx=20, pady=(20, 8))


def _plot_card(parent, fig, row):
    frame = ctk.CTkFrame(parent, fg_color=PANEL,
                         border_width=1, border_color=LINE, corner_radius=8)
    frame.grid(row=row, column=0, sticky="ew", padx=20, pady=(0, 4))
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="x", padx=2, pady=2)


class WaterQualityApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Surface Water Quality Assessment")
        self.geometry("1100x720")
        self.minsize(900, 600)
        self.configure(fg_color=SURFACE)

        # Two-column root grid: fixed left | expanding scrollable right
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._entries = {}
        self._open_figures = []
        self._result_panel = None
        self._error_frame = None
        self._error_lbl = None

        self._build_left_panel()
        self._build_right_scroll()
        self._show_placeholder()

    # ── Left panel (fixed, never scrolls) ─────────────────────────────────────

    def _build_left_panel(self):
        outer = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0,
                             border_width=0, width=LEFT_W)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_propagate(False)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)   # input list expands
        outer.rowconfigure(2, weight=0)   # button stays at bottom

        # Right border line
        ctk.CTkFrame(outer, fg_color=LINE, width=1, corner_radius=0).place(
            relx=1.0, rely=0, relheight=1.0, anchor="ne"
        )

        # ── header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(outer, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(24, 0))

        ctk.CTkLabel(
            header,
            text="MAMDANI FUZZY INFERENCE SYSTEM",
            text_color=ACCENT,
            font=ctk.CTkFont(family="Arial", size=10, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Surface Water\nQuality Assessment",
            text_color=INK,
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        # ── scrollable input list (scrollbar hidden) ──────────────────────────
        inputs = ctk.CTkScrollableFrame(
            outer, fg_color="transparent",
            scrollbar_button_color=LINE,
            scrollbar_button_hover_color=MUTED,
        )
        inputs.grid(row=1, column=0, sticky="nsew", padx=0, pady=(12, 0))
        inputs.columnconfigure(0, weight=1)
        inputs._scrollbar.grid_remove()

        # Error alert (hidden until needed)
        self._error_frame = ctk.CTkFrame(
            inputs, fg_color="#fff1ef", corner_radius=6,
            border_width=1, border_color="#f0c2bd",
        )
        self._error_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(0, 4))
        self._error_frame.grid_remove()
        self._error_lbl = ctk.CTkLabel(
            self._error_frame, text="",
            text_color="#9e2d22",
            font=ctk.CTkFont(family="Arial", size=11),
            wraplength=LEFT_W - 60,
        )
        self._error_lbl.pack(padx=12, pady=10)

        for field_row, (config_key, form_name) in enumerate(FORM_FIELDS, start=1):
            cfg = FUZZY_CONFIG[config_key]
            start, stop, _ = cfg["universe"]
            unit = cfg["unit"]

            cell = ctk.CTkFrame(inputs, fg_color="transparent")
            cell.grid(row=field_row, column=0, sticky="ew", padx=16, pady=6)

            ctk.CTkLabel(
                cell,
                text=f"{cfg['label']} ({unit})" if unit else cfg["label"],
                text_color=INK, anchor="w",
                font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            ).pack(fill="x", pady=(0, 6))

            entry = ctk.CTkEntry(
                cell, fg_color=PANEL, border_color=LINE, text_color=INK,
                font=ctk.CTkFont(family="Arial", size=12),
                height=38, corner_radius=6, border_width=1,
            )
            entry.pack(fill="x")
            self._entries[form_name] = entry

            hint = f"Valid range: {start:g} to {stop:g}" + (f" {unit}" if unit else "")
            ctk.CTkLabel(
                cell, text=hint, text_color=MUTED, anchor="w",
                font=ctk.CTkFont(family="Arial", size=10),
            ).pack(fill="x", pady=(3, 0))

        # ── assess button (pinned to bottom) ───────────────────────────────────
        btn_frame = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=0)
        btn_frame.grid(row=2, column=0, sticky="ew")
        ctk.CTkFrame(btn_frame, fg_color=LINE, height=1, corner_radius=0).pack(fill="x")
        ctk.CTkButton(
            btn_frame,
            text="Assess Water Quality",
            fg_color=ACCENT, hover_color=ACCENT_H, text_color="white",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            height=46, corner_radius=0,
            command=self._run_assessment,
        ).pack(fill="x")

    # ── Right scrollable area ──────────────────────────────────────────────────

    def _build_right_scroll(self):
        self._right = ctk.CTkScrollableFrame(
            self, fg_color=SURFACE,
            scrollbar_button_color=LINE,
            scrollbar_button_hover_color=MUTED,
        )
        self._right.grid(row=0, column=1, sticky="nsew")
        self._right.columnconfigure(0, weight=1)
        _enable_mousewheel(self._right)

    def _show_placeholder(self):
        ctk.CTkLabel(
            self._right,
            text='Enter parameter values on the left and press\n"Assess Water Quality" to see results.',
            text_color=MUTED,
            font=ctk.CTkFont(family="Arial", size=13),
            justify="center",
        ).grid(row=0, column=0, pady=60)

    # ── Assessment logic ───────────────────────────────────────────────────────

    def _run_assessment(self):
        self._error_frame.grid_remove()

        try:
            values = {}
            for config_key, form_name in FORM_FIELDS:
                raw = self._entries[form_name].get().strip()
                if not raw:
                    raise ValueError(f"{FUZZY_CONFIG[config_key]['label']} is required.")
                values[form_name] = float(raw)
        except ValueError as exc:
            self._error_lbl.configure(text=str(exc))
            self._error_frame.grid()
            return

        # Clear old results and figures
        for widget in self._right.winfo_children():
            widget.destroy()
        for fig in self._open_figures:
            plt.close(fig)
        self._open_figures.clear()

        score, label = evaluate(
            values["do"], values["ph"], values["turbidity"],
            values["nutrients"], values["temperature"], values["tds"],
        )
        self._show_results(score, label)

    def _show_results(self, score, label):
        right = self._right
        right.columnconfigure(0, weight=1)

        badge_bg = BADGE_COLORS.get(label, MUTED)
        badge_fg = BADGE_TEXT.get(label, "#ffffff")

        # ── result card ───────────────────────────────────────────────────────
        card = ctk.CTkFrame(right, fg_color=PANEL, corner_radius=8,
                            border_width=1, border_color=LINE)
        card.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))
        card.columnconfigure(0, weight=1)

        # result-summary
        summary = ctk.CTkFrame(card, fg_color="transparent")
        summary.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))

        left = ctk.CTkFrame(summary, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(
            left, text="WATER QUALITY INDEX",
            text_color=ACCENT,
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            left, text=f"{score:.2f}",
            text_color=INK,
            font=ctk.CTkFont(family="Arial", size=52, weight="bold"),
        ).pack(anchor="w")

        rite = ctk.CTkFrame(summary, fg_color="transparent")
        rite.pack(side="right")
        ctk.CTkLabel(
            rite, text=label,
            text_color=INK,
            font=ctk.CTkFont(family="Arial", size=30, weight="bold"),
        ).pack(anchor="e")
        ctk.CTkLabel(
            rite,
            text=f"  {label}  ",
            fg_color=badge_bg, text_color=badge_fg,
            corner_radius=999,
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
        ).pack(anchor="e", pady=(8, 0), ipadx=4, ipady=6)

        # divider
        ctk.CTkFrame(card, fg_color=LINE, height=1, corner_radius=0).grid(
            row=1, column=0, sticky="ew", padx=20, pady=(16, 0)
        )

        # interpretation
        ctk.CTkLabel(
            card,
            text=INTERPRETATIONS.get(label, ""),
            text_color=MUTED,
            font=ctk.CTkFont(family="Arial", size=13),
            justify="left", anchor="w",
            wraplength=680,
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(12, 4))

        # output score plot
        _h2(card, "Output Membership Plot", row=3)
        fig1 = _build_output_figure(score)
        self._open_figures.append(fig1)
        _plot_card(card, fig1, row=4)

        # combined membership plot
        _h2(card, "All Membership Functions", row=5)
        fig2 = _build_combined_figure()
        self._open_figures.append(fig2)
        _plot_card(card, fig2, row=6)

        ctk.CTkFrame(card, fg_color="transparent", height=20).grid(row=7, column=0)

        # bottom padding in scroll area
        ctk.CTkFrame(right, fg_color="transparent", height=24).grid(
            row=1, column=0, sticky="ew"
        )

        _save_figures(fig1, fig2)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    app = WaterQualityApp()
    app.mainloop()
