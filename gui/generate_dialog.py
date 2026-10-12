from __future__ import annotations
import math
import tkinter as tk
from tkinter import messagebox, ttk

from dsp.task2_ops import generate_wave, nyquist_rate


class GenerateDialog(tk.Toplevel):
    """Dialog for generating a sine or cosine signal.

    The menu item / button that opens it decides which wave type is
    pre-selected, but the user can still switch it with the radio buttons.
    """

    def __init__(self, app, kind: str = "sine"):
        super().__init__(app)
        self.app = app
        self.title("Generate signal")
        self.resizable(False, False)
        self.transient(app)

        self.kind = tk.StringVar(value=kind)
        self.amplitude = tk.StringVar(value="1")
        self.phase = tk.StringVar(value="0")
        self.phase_unit = tk.StringVar(value="rad")
        self.frequency = tk.StringVar(value="5")
        self.fs = tk.StringVar(value="50")
        self.duration = tk.StringVar(value="1")

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Wave type:").grid(row=0, column=0, sticky="w", pady=3)
        types = ttk.Frame(frm)
        types.grid(row=0, column=1, columnspan=2, sticky="w")
        ttk.Radiobutton(types, text="Sine", value="sine", variable=self.kind).pack(side="left")
        ttk.Radiobutton(types, text="Cosine", value="cosine", variable=self.kind).pack(
            side="left", padx=(12, 0))

        rows = [("Amplitude A:", self.amplitude, ""),
                ("Phase shift \u03b8:", self.phase, None),     # unit chooser
                ("Analog frequency f:", self.frequency, "Hz"),
                ("Sampling frequency fs:", self.fs, "Hz"),
                ("Duration:", self.duration, "s")]
        self.entries = []
        for r, (label, var, unit) in enumerate(rows, start=1):
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="w", pady=3)
            e = ttk.Entry(frm, textvariable=var, width=12)
            e.grid(row=r, column=1, sticky="w", padx=6)
            self.entries.append(e)
            if unit is None:
                ttk.Combobox(frm, textvariable=self.phase_unit, values=("rad", "deg"),
                             width=5, state="readonly").grid(row=r, column=2, sticky="w")
            else:
                ttk.Label(frm, text=unit).grid(row=r, column=2, sticky="w")

        self.hint = ttk.Label(frm, text="", wraplength=300, justify="left")
        self.hint.grid(row=6, column=0, columnspan=3, sticky="w", pady=(8, 4))

        btns = ttk.Frame(frm)
        btns.grid(row=7, column=0, columnspan=3, sticky="e", pady=(6, 0))
        ttk.Button(btns, text="Generate", command=self.generate).pack(side="left", padx=4)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="left")

        for var in (self.frequency, self.fs, self.kind):
            var.trace_add("write", lambda *_: self._refresh())
        self._refresh()

        self.bind("<Return>", lambda e: self.generate())
        self.bind("<Escape>", lambda e: self.destroy())
        self.entries[0].focus_set()
        self.grab_set()

    # ---------- helpers ----------
    def _refresh(self):
        """Update the window title and the live sampling-theorem hint."""
        self.title(f"Generate {self.kind.get()} wave")
        try:
            f, fs = float(self.frequency.get()), float(self.fs.get())
        except ValueError:
            self.hint.configure(text="Sampling theorem: fs \u2265 2f", foreground="gray40")
            return
        need = nyquist_rate(f)
        if fs < need:
            self.hint.configure(
                text=f"fs is too low. Sampling theorem needs fs \u2265 2f = {need:g} Hz.",
                foreground="red")
        elif fs == need:
            self.hint.configure(
                text=f"fs = 2f is the bare minimum ({need:g} Hz); samples may miss the peaks.",
                foreground="darkorange")
        else:
            self.hint.configure(
                text=f"OK: fs = {fs:g} Hz \u2265 2f = {need:g} Hz.", foreground="darkgreen")

    @staticmethod
    def _number(text: str, label: str) -> float:
        try:
            value = float(text)
        except ValueError:
            raise ValueError(f"'{label}' must be a number (got '{text}').") from None
        if not math.isfinite(value):
            raise ValueError(f"'{label}' must be a finite number.")
        return value

    # ---------- action ----------
    def generate(self):
        try:
            amplitude = self._number(self.amplitude.get(), "Amplitude")
            phase = self._number(self.phase.get(), "Phase shift")
            if self.phase_unit.get() == "deg":
                phase = math.radians(phase)
            f = self._number(self.frequency.get(), "Analog frequency")
            fs = self._number(self.fs.get(), "Sampling frequency")
            duration = self._number(self.duration.get(), "Duration")

            if f > 0 and fs == nyquist_rate(f) and not messagebox.askokcancel(
                    "Sampling frequency", "fs equals exactly 2f (the minimum allowed).\n"
                    "The samples may miss the peaks of the wave.\n\nContinue?", parent=self):
                return
            signal = generate_wave(self.kind.get(), amplitude, f, fs, phase, duration)
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc), parent=self)
            return

        # select_only=False: generated signals stay selected together, so
        # generating a second wave displays both at the same time.
        self.app.add_signal(signal, select_only=False)
        self.app.set_status(f"Generated '{signal.name}' ({len(signal)} samples)")
        self.destroy()
