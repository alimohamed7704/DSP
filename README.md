# Digital Signal Processing Toolkit

Python + Tkinter + matplotlib. Every task is a tab in the same GUI.

```
pip install -r requirements.txt
python main.py
```
(Tkinter ships with Python; on Debian/Ubuntu install it with `sudo apt install python3-tk`.)

## Task 1 - Basic operations
Load signals from `.txt` (first row `N`, then `index value` rows), plot them, add any number of
signals, subtract, multiply by a constant, delay/advance `x(n-k)` / `x(n+k)`, fold `x(-n)`.

## Task 2 - Signal generation
* **Signal Generation** menu -> *Sine wave* / *Cosine wave* (also available as buttons on the Task 2 tab).
  Choose amplitude `A`, phase shift `θ` (rad or deg), analog frequency `f`, sampling frequency `fs`
  and duration. `x(n) = A·sin|cos(2π·f·n/fs + θ)`.
* The sampling theorem is enforced: `fs < 2f` is rejected (live hint in the dialog); `fs = 2f` asks for confirmation.
* **Representation**: display signals as *discrete* (stem) or *continuous* (curve).
  Generated waves are drawn as the true analog waveform; other signals are drawn by joining their samples.
* **Multiple signals**: select two (or more) signals in the list to show them together, either
  *overlaid* on one plot or *stacked* in separate plots.

## Project layout
```
main.py              entry point
dsp/                 signal processing (no GUI code)
  signal.py          Signal (+ WaveParams for generated waves)
  io.py              read / write signal files
  task1_ops.py       Task 1 operations
  task2_ops.py       Task 2 sine / cosine generation + sampling-theorem check
gui/
  app.py             main window, menu, TABS list (register new task tabs here)
  plotting.py        matplotlib panel (discrete / continuous, overlay / stacked)
  task1_tab.py       Task 1 tab
  task2_tab.py       Task 2 tab
  generate_dialog.py sine / cosine generation dialog
data/signals/        sample input files
```
