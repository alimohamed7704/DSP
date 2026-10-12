from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from dsp.signal import Signal

DISCRETE = "discrete"
CONTINUOUS = "continuous"
OVERLAY = "overlay"      # all signals on one axes
STACKED = "stacked"      # one axes per signal, sharing the n axis


class PlotPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        NavigationToolbar2Tk(self.canvas, self).update()   # zoom / pan toolbar
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.plot([])

    def plot(self, signals: list[Signal], mode: str = DISCRETE, layout: str = OVERLAY):
        """Draw the signals.

        mode   -- DISCRETE (stem plot) or CONTINUOUS (smooth curve)
        layout -- OVERLAY (same axes) or STACKED (one subplot per signal)
        """
        fig = self.figure
        fig.clear()
        items = list(enumerate(signals))        # keep a stable colour per signal

        if layout == STACKED and len(items) > 1:
            axes = fig.subplots(len(items), 1, sharex=True, squeeze=False)[:, 0]
            groups = [[it] for it in items]
        else:
            axes = [fig.add_subplot(111)]
            groups = [items]

        for ax, group in zip(axes, groups):
            self._draw(ax, group, mode)
        axes[-1].set_xlabel("n")
        fig.tight_layout()
        self.canvas.draw_idle()

    @staticmethod
    def _draw(ax, items, mode):
        for i, s in items:
            color = f"C{i % 10}"
            if mode == CONTINUOUS:
                x, y = s.continuous()
                ax.plot(x, y, color=color, label=s.name)
            else:
                markerline, stemlines, _ = ax.stem(
                    s.indices, s.values, label=s.name, basefmt=" ")
                markerline.set_color(color)
                stemlines.set_color(color)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axvline(0, color="gray", linewidth=0.6, linestyle="--")
        ax.set_ylabel("x(n)")
        ax.grid(True, alpha=0.3)
        if items:
            ax.legend(loc="best", fontsize="small")
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
