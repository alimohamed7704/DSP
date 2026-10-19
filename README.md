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

## Task 3 - Quantization
Select **one** signal in the list, open the **Task 3** tab, choose the resolution and click
**Quantize selected signal**.

* **Resolution**: enter either the *number of levels* `L` or the *number of bits* `b`.
  With bits, `L = 2^b`. A live hint shows the derived value (bits -> levels, or levels -> bits).
  If `L` is not a power of two, the code uses `ceil(log2 L)` bits.
* **Method** (uniform quantizer, mid-point reconstruction):
  * step `Δ = (max - min) / L`
  * interval `i = floor((x - min) / Δ)`, with the maximum sample placed in the last interval
  * quantized value `xq = min + (i + 0.5)·Δ`
  * quantization error `e = xq - x` (always within `±Δ/2`)
  * encoded value = `i` written in binary with `ceil(log2 L)` bits
* **Output**:
  * the quantized signal and the error are added to the signal list as `<name>_quantized` and
    `<name>_error` (so they can be used in other tasks), and the main plot shows the original
    together with the quantized signal;
  * a results window shows the original vs. quantized signal (with the quantization levels), the
    quantization error with its `±Δ/2` limits, and a table with the **encoded signal**
    (`n`, `x(n)`, interval, binary code, `xq(n)`, error).
* **Save encoded signal...** writes a text file: first row `N`, then one `index code` row per sample.
* Limits: `2 <= L <= 65536` (up to 16 bits). A constant signal quantizes to itself with zero error.

## Project layout
```
main.py              entry point
dsp/                 signal processing (no GUI code)
  signal.py          Signal (+ WaveParams for generated waves)
  io.py              read / write signal files, write encoded signals
  task1_ops.py       Task 1 operations
  task2_ops.py       Task 2 sine / cosine generation + sampling-theorem check
  task3_ops.py       Task 3 quantization (levels / bits, error, binary encoding)
gui/
  app.py             main window, menu, TABS list (register new task tabs here)
  plotting.py        matplotlib panel (discrete / continuous, overlay / stacked)
  task1_tab.py       Task 1 tab
  task2_tab.py       Task 2 tab
  task3_tab.py       Task 3 tab
  quantization_view.py  Task 3 results window (plots + encoded table)
  generate_dialog.py sine / cosine generation dialog
tests/               unit tests: python -m unittest discover -s tests -t .
data/signals/        sample input files
```
