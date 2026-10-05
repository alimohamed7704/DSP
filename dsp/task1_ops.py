from __future__ import annotations
import numpy as np
from .signal import Signal


def add_signals(*signals: Signal, name: str | None = None) -> Signal:
    """Sum any number of signals. Missing samples count as 0."""
    if not signals:
        raise ValueError("Need at least one signal")
    all_idx = np.unique(np.concatenate([s.indices for s in signals]))
    total = np.zeros(len(all_idx))
    for s in signals:
        total[np.searchsorted(all_idx, s.indices)] += s.values
    return Signal(all_idx, total, name or " + ".join(s.name for s in signals))


def scale(signal: Signal, c: float, name: str | None = None) -> Signal:
    return Signal(signal.indices.copy(), signal.values * c, name or f"{c:g}*{signal.name}")


def subtract(a: Signal, b: Signal, name: str | None = None) -> Signal:
    """a - b = a + (-1)*b, as the task hint suggests."""
    return add_signals(a, scale(b, -1), name=name or f"{a.name} - {b.name}")


def delay(signal: Signal, k: int, name: str | None = None) -> Signal:
    """x(n-k): shift right by k."""
    return Signal(signal.indices + int(k), signal.values.copy(), name or f"{signal.name}(n-{k})")


def advance(signal: Signal, k: int, name: str | None = None) -> Signal:
    """x(n+k): shift left by k."""
    return Signal(signal.indices - int(k), signal.values.copy(), name or f"{signal.name}(n+{k})")


def fold(signal: Signal, name: str | None = None) -> Signal:
    """x(-n): reverse about n = 0."""
    return Signal(-signal.indices, signal.values.copy(), name or f"{signal.name}(-n)")