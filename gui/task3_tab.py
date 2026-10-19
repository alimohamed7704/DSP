from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk

from dsp import task3_ops as q
from gui.quantization_view import QuantizationWindow


class Task3Tab(ttk.Frame):
    title = "Task 3 - Quantization"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.by = tk.StringVar(value="levels")      # "levels" or "bits"
        self.amount = tk.StringVar(value="8")

        # what the user specifies: number of levels OR number of bits
        f = ttk.LabelFrame(self, text="Quantization resolution")
        f.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        ttk.Radiobutton(f, text="Number of levels", value="levels",
                        variable=self.by).grid(row=0, column=0, sticky="w", padx=8, pady=2)
        ttk.Radiobutton(f, text="Number of bits", value="bits",
                        variable=self.by).grid(row=1, column=0, sticky="w", padx=8, pady=2)
        ttk.Entry(f, textvariable=self.amount, width=8).grid(row=0, column=1, rowspan=2, padx=8)
        self.hint = ttk.Label(f, text="")
        self.hint.grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 4))
        self.by.trace_add("write", self._update_hint)
        self.amount.trace_add("write", self._update_hint)
        self._update_hint()

        g = ttk.LabelFrame(self, text="Apply")
        g.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        ttk.Button(g, text="Quantize selected signal", command=self.quantize).pack(
            fill="x", padx=6, pady=3)
        ttk.Label(g, text="(select exactly one signal)").pack(padx=6)

    def _update_hint(self, *_):
        """Show the derived value: bits -> levels, or levels -> bits per sample."""
        try:
            v = int(self.amount.get())
            if self.by.get() == "bits":
                self.hint.config(text=f"= {q.bits_to_levels(v)} levels")
            else:
                self.hint.config(text=f"= {q.levels_to_bits(v)} bits per sample")
        except ValueError:
            self.hint.config(text="")

    def quantize(self):
        self.app.run_safely(self._quantize)

    def _quantize(self):
        sel = self.app.selected_signals()
        if len(sel) != 1:
            messagebox.showinfo("Quantization", "Select exactly one signal to quantize.")
            return
        try:
            amount = int(self.amount.get())
        except ValueError:
            raise ValueError("Enter a whole number of levels / bits.")
        original = sel[0]
        if self.by.get() == "bits":
            res = q.quantize(original, bits=amount)
        else:
            res = q.quantize(original, levels=amount)

        # keep the results in the signal list so other tasks can use them
        self.app.add_signal(res.quantized, select_only=False)
        self.app.add_signal(res.error, select_only=False)
        # main plot: original + quantized together
        lb = self.app.listbox
        lb.selection_clear(0, "end")
        for i, s in enumerate(self.app.signals):
            if s is original or s is res.quantized:
                lb.selection_set(i)
        self.app.refresh_plot()
        self.app.set_status(f"Quantized '{original.name}': {res.levels} levels, "
                            f"{res.bits} bits, step {res.step:.4g}")
        QuantizationWindow(self.app, res)
