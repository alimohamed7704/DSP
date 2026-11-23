from __future__ import annotations

import numpy as np

from .signal import Signal


def _dense(signal: Signal) -> tuple[int, np.ndarray]:
    """(first index, values) on a gap-free grid; missing samples are 0."""
    if len(signal) == 0:
        raise ValueError(f"'{signal.name}' is empty.")
    first = int(signal.indices[0])
    values = np.zeros(int(signal.indices[-1]) - first + 1)
    values[signal.indices - first] = signal.values
    return first, values


def _common_fs(*signals: Signal):
    """fs shared by all signals, or None if unknown / different."""
    rates = {s.fs for s in signals}
    return rates.pop() if len(rates) == 1 else None


# ---------- 1) moving average ----------
def moving_average(signal: Signal, window: int, name: str | None = None) -> Signal:
    if window != int(window) or window < 1:
        raise ValueError("Window size must be a whole number of at least 1.")
    window = int(window)
    first, x = _dense(signal)
    if window > len(x):
        raise ValueError(f"Window size ({window}) is larger than the signal "
                         f"({len(x)} samples).")
    # running sum: prefix[i + M] - prefix[i] = x[i] + ... + x[i + M - 1]
    prefix = np.concatenate(([0.0], np.cumsum(x)))
    y = (prefix[window:] - prefix[:-window]) / window
    idx = first + np.arange(len(y))
    return Signal(idx, y, name or f"{signal.name}_MA{window}", fs=signal.fs)


# ---------- 2) sharpening ----------
def first_derivative(signal: Signal, name: str | None = None) -> Signal:
    """y(n) = x(n) - x(n-1)."""
    first, x = _dense(signal)
    if len(x) < 2:
        raise ValueError("The first derivative needs at least 2 samples.")
    y = x[1:] - x[0:-1]
    idx = first + np.arange(len(y))
    return Signal(idx, y, name or f"{signal.name}_d1", fs=signal.fs)


def second_derivative(signal: Signal, name: str | None = None) -> Signal:
    """y(n) = x(n+1) - 2x(n) + x(n-1)."""
    first, x = _dense(signal)
    if len(x) < 3:
        raise ValueError("The second derivative needs at least 3 samples.")
    y = x[2:] - 2 * x[1:-1] + x[:-2]
    idx = first  + np.arange(len(y))
    return Signal(idx, y, name or f"{signal.name}_d2", fs=signal.fs)


# ---------- 3) convolution ----------
def convolve(a: Signal, b: Signal, name: str | None = None) -> Signal:
    """Linear convolution y(n) = sum_k a(k) b(n-k), computed straight from the definition."""
    first_a, xa = _dense(a)
    first_b, xb = _dense(b)
    y = np.zeros(len(xa) + len(xb) - 1)
    for k, ak in enumerate(xa):          # each input sample adds a scaled copy of b
        y[k:k + len(xb)] += ak * xb
    idx = first_a + first_b + np.arange(len(y))
    return Signal(idx, y, name or f"{a.name} * {b.name}", fs=_common_fs(a, b))
