from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from dsp.io import read_signal, write_signal
from dsp.signal import Signal
from gui.generate_dialog import GenerateDialog
from gui.plotting import DISCRETE, N_AXIS, OVERLAY, TIME_AXIS, PlotPanel
from gui.task1_tab import Task1Tab
from gui.task2_tab import Task2Tab

# Every task adds its tab here. Each class needs a `title` and a
# (parent, app) constructor.
TABS = [Task1Tab, Task2Tab]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Digital Signal Processing Toolkit")
        self.geometry("1100x700")
        self.signals: list[Signal] = []
        self.display_mode = tk.StringVar(value=DISCRETE)   # discrete / continuous
        self.plot_layout = tk.StringVar(value=OVERLAY)     # overlay / stacked
        self.x_axis = tk.StringVar(value=N_AXIS)           # n / time

        self._build_menu()
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        self._build_sidebar(paned)

        right = ttk.Frame(paned)
        paned.add(right, weight=4)
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill=tk.X, padx=6, pady=6)
        for tab_cls in TABS:
            self.notebook.add(tab_cls(self.notebook, self), text=tab_cls.title)

        # Global x-axis selector: applies to every task, since all tabs share one plot
        axis_bar = ttk.Frame(right)
        axis_bar.pack(fill=tk.X, padx=6)
        ttk.Label(axis_bar, text="X axis:").pack(side=tk.LEFT)
        for text, value in (("Sample index (n)", N_AXIS), ("Time (t = n / fs)", TIME_AXIS)):
            ttk.Radiobutton(axis_bar, text=text, value=value, variable=self.x_axis,
                            command=self.refresh_plot).pack(side=tk.LEFT, padx=6)

        self.plot_panel = PlotPanel(right)
        self.plot_panel.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        self.status = tk.StringVar(value="Load a signal to begin.")
        ttk.Label(self, textvariable=self.status, relief=tk.SUNKEN, anchor=tk.W).pack(
            fill=tk.X, side=tk.BOTTOM)

    # ---------- menu ----------
    def _build_menu(self):
        menubar = tk.Menu(self, tearoff=False)
        gen = tk.Menu(menubar, tearoff=False)
        gen.add_command(label="Sine wave", command=lambda: self.open_generator("sine"))
        gen.add_command(label="Cosine wave", command=lambda: self.open_generator("cosine"))
        menubar.add_cascade(label="Signal Generation", menu=gen)
        self.config(menu=menubar)

    def open_generator(self, kind: str):
        GenerateDialog(self, kind)

    # ---------- sidebar ----------
    def _build_sidebar(self, paned):
        side = ttk.LabelFrame(paned, text="Signals (Ctrl/Shift-click to multi-select)")
        paned.add(side, weight=1)
        self.listbox = tk.Listbox(side, selectmode=tk.EXTENDED, exportselection=False, width=28)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.refresh_plot())
        for text, cmd in [("Load from file...", self.load_file),
                          ("Save selected...", self.save_selected),
                          ("Remove selected", self.remove_selected)]:
            ttk.Button(side, text=text, command=cmd).pack(fill=tk.X, padx=6, pady=2)

    # ---------- API used by task tabs ----------
    def selected_signals(self) -> list[Signal]:
        return [self.signals[i] for i in self.listbox.curselection()]

    def add_signal(self, signal: Signal, select_only: bool = True):
        signal.name = self._unique_name(signal.name)
        self.signals.append(signal)
        self.listbox.insert(tk.END, signal.name)
        if select_only:
            self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(tk.END)
        self.refresh_plot()

    def refresh_plot(self):
        sel = self.selected_signals()
        if self.x_axis.get() == TIME_AXIS and any(s.fs is None for s in sel):
            self.set_status("Time axis needs a sampling frequency for every selected "
                            "signal (files have none) - showing n instead.")
        self.plot_panel.plot(sel, mode=self.display_mode.get(),
                             layout=self.plot_layout.get(), x_axis=self.x_axis.get())

    def set_status(self, msg: str):
        self.status.set(msg)

    def run_safely(self, func):
        """Run func(); show errors in a dialog instead of crashing."""
        try:
            func()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    # ---------- file actions ----------
    def load_file(self):
        paths = filedialog.askopenfilenames(
            title="Open signal file(s)", filetypes=[("Text files", "*.txt"), ("All", "*.*")])
        for P in paths:
            self.run_safely(lambda p=P: self._load_one(P))

    def _load_one(self, path):
        sig = read_signal(path)
        self.add_signal(sig, select_only=False)
        self.set_status(f"Loaded '{sig.name}' ({len(sig)} samples)")

    def save_selected(self):
        sel = self.selected_signals()
        if len(sel) != 1:
            messagebox.showinfo("Save", "Select exactly one signal to save.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile=sel[0].name.replace(" ", "_") + ".txt")
        if path:
            self.run_safely(lambda: write_signal(sel[0], path))

    def remove_selected(self):
        for i in reversed(self.listbox.curselection()):
            self.listbox.delete(i)
            del self.signals[i]
        self.refresh_plot()

    def _unique_name(self, name: str) -> str:
        existing = {s.name for s in self.signals}
        if name not in existing:
            return name
        n = 2
        while f"{name} ({n})" in existing:
            n += 1
        return f"{name} ({n})"