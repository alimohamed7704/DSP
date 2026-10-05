from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from dsp.signal import Signal


class PlotPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        NavigationToolbar2Tk(self.canvas, self).update()   # zoom / pan toolbar
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.plot([])

    def plot(self, signals: list[Signal]):
        ax = self.ax
        ax.clear()
        for i, s in enumerate(signals):
            color = f"C{i % 10}"
            markerline, stemlines, _ = ax.stem(s.indices, s.values, label=s.name, basefmt=" ")
            markerline.set_color(color)
            stemlines.set_color(color)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axvline(0, color="gray", linewidth=0.6, linestyle="--")
        ax.set_xlabel("n")
        ax.set_ylabel("x(n)")
        ax.grid(True, alpha=0.3)
        if signals:
            ax.legend(loc="best")
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.canvas.draw_idle()