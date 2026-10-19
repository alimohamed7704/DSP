"""Results window for Task 3: plots (original / quantized / error) + encoded table."""
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from dsp.io import write_encoded
from dsp.task3_ops import QuantizationResult
from gui.plotting import TIME_AXIS

MAX_LEVEL_LINES = 32        # more horizontal level lines than this just clutters the plot


def _stem(ax, x, y, color, label):
    markerline, stemlines, _ = ax.stem(x, y, label=label, basefmt=" ")
    markerline.set_color(color)
    stemlines.set_color(color)


def draw_quantization(fig, res: QuantizationResult, use_time: bool = False):
    """Top: original vs quantized (+ level lines). Bottom: quantization error."""
    fig.clear()
    ax1, ax2 = fig.subplots(2, 1, sharex=True)
    x = res.original.time_axis() if use_time else res.original.indices

    _stem(ax1, x, res.original.values, "C0", "original")
    _stem(ax1, x, res.quantized.values, "C1", "quantized")
    if res.levels <= MAX_LEVEL_LINES:
        for v in res.level_values:
            ax1.axhline(v, color="gray", linewidth=0.5, linestyle=":")
    ax1.set_title(f"{res.levels} levels ({res.bits} bits), step = {res.step:.4g}")
    ax1.set_ylabel("x(n)")
    ax1.legend(loc="best", fontsize="small")

    _stem(ax2, x, res.error.values, "C3", "error")
    for b in (res.step / 2, -res.step / 2):         # the error can never exceed +-step/2
        ax2.axhline(b, color="gray", linewidth=0.8, linestyle="--")
    ax2.set_title("Quantization error  (quantized - original)")
    ax2.set_ylabel("error")
    ax2.set_xlabel("t (s)" if use_time else "n")

    for ax in (ax1, ax2):
        ax.axhline(0, color="black", linewidth=0.8)
        ax.grid(True, alpha=0.3)
    if not use_time:
        ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
    fig.tight_layout()


class QuantizationWindow(tk.Toplevel):
    def __init__(self, app, result: QuantizationResult):
        super().__init__(app)
        self.res = result
        self.title(f"Quantization - {result.original.name}")
        self.geometry("900x760")

        use_time = app.x_axis.get() == TIME_AXIS and result.original.fs is not None
        fig = Figure(figsize=(8, 4.5), dpi=100)
        canvas = FigureCanvasTkAgg(fig, master=self)
        NavigationToolbar2Tk(canvas, self).update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        draw_quantization(fig, result, use_time)
        canvas.draw_idle()

        # table: the encoded signal next to the other quantities
        box = ttk.LabelFrame(self, text="Encoded signal")
        box.pack(fill=tk.X, padx=6, pady=(0, 6))
        cols = ("n", "x(n)", "interval", "code", "xq(n)", "error")
        table = ttk.Treeview(box, columns=cols, show="headings", height=7)
        for c in cols:
            table.heading(c, text=c)
            table.column(c, width=110, anchor="center")
        for n, x, i, code, xq, e in zip(result.original.indices, result.original.values,
                                        result.level_indices, result.codes,
                                        result.quantized.values, result.error.values):
            table.insert("", tk.END, values=(int(n), f"{x:.6g}", int(i), code,
                                             f"{xq:.6g}", f"{e:.6g}"))
        scroll = ttk.Scrollbar(box, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        table.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Button(bar, text="Save encoded signal...", command=self.save_encoded).pack(side=tk.LEFT)
        ttk.Button(bar, text="Close", command=self.destroy).pack(side=tk.RIGHT)

    def save_encoded(self):
        path = filedialog.asksaveasfilename(
            parent=self, defaultextension=".txt",
            initialfile=self.res.original.name.replace(" ", "_") + "_encoded.txt")
        if path:
            write_encoded(self.res.original.indices, self.res.codes, path)
