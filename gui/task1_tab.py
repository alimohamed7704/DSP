from __future__ import annotations
from tkinter import messagebox, ttk

from dsp import task1_ops as ops

class Task1Tab(ttk.Frame):
    title = "Task 1 - Basic operations"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Add / subtract
        f = ttk.LabelFrame(self, text="Combine signals")
        f.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        ttk.Button(f, text="Add selected (2 or more)", command=self.add).pack(fill="x", padx=6, pady=3)
        ttk.Button(f, text="Subtract: 1st selected - 2nd", command=self.subtract).pack(fill="x", padx=6, pady=3)
        ttk.Label(f, text="(order = order in the list)").pack(padx=6)

        # Multiply
        f = ttk.LabelFrame(self, text="Amplify / reduce")
        f.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        ttk.Label(f, text="Constant:").pack(side="left", padx=6)
        self.const = ttk.Entry(f, width=8)
        self.const.insert(0, "2")
        self.const.pack(side="left", padx=3)
        ttk.Button(f, text="Multiply", command=self.multiply).pack(side="left", padx=6, pady=6)

        # Delay / advance
        f = ttk.LabelFrame(self, text="Delay / advance")
        f.grid(row=0, column=2, padx=6, pady=6, sticky="nsew")
        ttk.Label(f, text="k:").grid(row=0, column=0, padx=6)
        self.k = ttk.Entry(f, width=6)
        self.k.insert(0, "2")
        self.k.grid(row=0, column=1)
        ttk.Button(f, text="Delay x(n-k)", command=self.delay).grid(
            row=1, column=0, columnspan=2, padx=6, pady=2, sticky="ew")
        ttk.Button(f, text="Advance x(n+k)", command=self.advance).grid(
            row=2, column=0, columnspan=2, padx=6, pady=2, sticky="ew")

        # Fold
        f = ttk.LabelFrame(self, text="Fold")
        f.grid(row=0, column=3, padx=6, pady=6, sticky="nsew")
        ttk.Button(f, text="Fold x(-n)", command=self.fold).pack(padx=6, pady=6)

    # ---------- helpers ----------
    def _need(self, count=None, at_least=None):
        sel = self.app.selected_signals()
        if count is not None and len(sel) != count:
            messagebox.showinfo("Selection", f"Select exactly {count} signal(s).")
            return None
        if at_least is not None and len(sel) < at_least:
            messagebox.showinfo("Selection", f"Select at least {at_least} signal(s).")
            return None
        return sel

    def _show(self, result):
        self.app.add_signal(result)
        self.app.set_status(f"Result: {result.name}")

    def _apply_each(self, func):
        """Apply a one-signal operation to every selected signal."""
        sel = self._need(at_least=1)
        if sel is None:
            return
        results = [func(s) for s in sel]
        for r in results:
            self.app.add_signal(r, select_only=False)
        self.app.listbox.selection_clear(0, "end")
        for i in range(len(results)):
            self.app.listbox.selection_set(len(self.app.signals) - 1 - i)
        self.app.refresh_plot()
        self.app.set_status("Result: " + ", ".join(r.name for r in results))

    # ---------- actions ----------
    def add(self):
        sel = self._need(at_least=2)
        if sel:
            self._show(ops.add_signals(*sel))

    def subtract(self):
        sel = self._need(count=2)
        if sel:
            self._show(ops.subtract(sel[0], sel[1]))

    def multiply(self):
        self.app.run_safely(
            lambda: self._apply_each(lambda s: ops.scale(s, float(self.const.get()))))

    def delay(self):
        self.app.run_safely(
            lambda: self._apply_each(lambda s: ops.delay(s, int(self.k.get()))))

    def advance(self):
        self.app.run_safely(
            lambda: self._apply_each(lambda s: ops.advance(s, int(self.k.get()))))

    def fold(self):
        self._apply_each(ops.fold)