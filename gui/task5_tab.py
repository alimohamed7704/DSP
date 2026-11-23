from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk

from dsp import task5_ops as ops


class Task5Tab(ttk.Frame):
    title = "Task 5 - Averaging & convolution"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.window = tk.StringVar(value="3")

        # 1) Moving average: the user chooses the number of points averaged
        f = ttk.LabelFrame(self, text="Moving average")
        f.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        ttk.Label(f, text="Window size (points):").grid(row=0, column=0, padx=6, pady=3)
        ttk.Entry(f, textvariable=self.window, width=6).grid(row=0, column=1, padx=3)
        ttk.Button(f, text="Moving average", command=self.moving_average).grid(
            row=1, column=0, columnspan=2, padx=6, pady=3, sticky="ew")
        ttk.Label(f, text="y(n) = mean of x(n) ... x(n+M-1)").grid(
            row=2, column=0, columnspan=2, padx=6)

        # 2) Sharpening: first and second derivative
        f = ttk.LabelFrame(self, text="Sharpening")
        f.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        ttk.Button(f, text="First derivative", command=self.first_derivative).pack(
            fill="x", padx=6, pady=3)
        ttk.Label(f, text="y(n) = x(n) - x(n-1)").pack(padx=6)
        ttk.Button(f, text="Second derivative", command=self.second_derivative).pack(
            fill="x", padx=6, pady=(6, 3))
        ttk.Label(f, text="y(n) = x(n+1) - 2x(n) + x(n-1)").pack(padx=6)

        # 3) Convolution of two signals
        f = ttk.LabelFrame(self, text="Convolution")
        f.grid(row=0, column=2, padx=6, pady=6, sticky="nsew")
        ttk.Button(f, text="Convolve selected (2 signals)", command=self.convolve).pack(
            fill="x", padx=6, pady=3)
        ttk.Label(f, text="y(n) = sum  a(k) b(n-k)").pack(padx=6)

        ttk.Label(self, text="Moving average and sharpening apply to every selected signal; "
                             "convolution needs exactly two.").grid(
            row=1, column=0, columnspan=3, sticky="w", padx=8)

    # ---------- helpers ----------
    def _show(self, results):
        """Add the results to the signal list and plot only them."""
        for r in results:
            self.app.add_signal(r, select_only=False)
        lb = self.app.listbox
        lb.selection_clear(0, "end")
        for i in range(len(self.app.signals) - len(results), len(self.app.signals)):
            lb.selection_set(i)
        self.app.refresh_plot()
        self.app.set_status("Result: " + ", ".join(r.name for r in results))

    def _apply_each(self, func):
        sel = self.app.selected_signals()
        if not sel:
            messagebox.showinfo("Selection", "Select at least 1 signal.")
            return
        self._show([func(s) for s in sel])      # compute all first: nothing added on error

    # ---------- actions ----------
    def moving_average(self):
        def run():
            try:
                m = int(self.window.get())
            except ValueError:
                raise ValueError("Enter the window size as a whole number.")
            self._apply_each(lambda s: ops.moving_average(s, m))
        self.app.run_safely(run)

    def first_derivative(self):
        self.app.run_safely(lambda: self._apply_each(ops.first_derivative))

    def second_derivative(self):
        self.app.run_safely(lambda: self._apply_each(ops.second_derivative))

    def convolve(self):
        def run():
            sel = self.app.selected_signals()
            if len(sel) != 2:
                messagebox.showinfo("Selection", "Select exactly 2 signals to convolve.")
                return
            self._show([ops.convolve(sel[0], sel[1])])
        self.app.run_safely(run)
