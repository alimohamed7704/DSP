from __future__ import annotations
from tkinter import ttk

from gui.plotting import CONTINUOUS, DISCRETE, OVERLAY, STACKED


class Task2Tab(ttk.Frame):
    title = "Task 2 - Signal generation"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Continuous / discrete representation
        f = ttk.LabelFrame(self, text="Representation")
        f.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        for text, value in (("Discrete (stem)", DISCRETE), ("Continuous (curve)", CONTINUOUS)):
            ttk.Radiobutton(f, text=text, value=value, variable=app.display_mode,
                            command=app.refresh_plot).pack(anchor="w", padx=8, pady=2)

        # Two signals at the same time: one set of axes or one per signal
        f = ttk.LabelFrame(self, text="Multiple signals")
        f.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        for text, value in (("Overlay (same plot)", OVERLAY), ("Stacked (separate plots)", STACKED)):
            ttk.Radiobutton(f, text=text, value=value, variable=app.plot_layout,
                            command=app.refresh_plot).pack(anchor="w", padx=8, pady=2)

        # Same actions as the Signal Generation menu
        f = ttk.LabelFrame(self, text="Signal Generation")
        f.grid(row=0, column=2, padx=6, pady=6, sticky="nsew")
        ttk.Button(f, text="Sine wave...", command=lambda: app.open_generator("sine")).pack(
            fill="x", padx=6, pady=3)
        ttk.Button(f, text="Cosine wave...", command=lambda: app.open_generator("cosine")).pack(
            fill="x", padx=6, pady=3)
        ttk.Label(f, text="(or use the Signal Generation menu)").pack(padx=6)
