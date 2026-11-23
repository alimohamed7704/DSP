"""Task 3: uniform quantization of a signal (no GUI code here).

Method (mid-point reconstruction):
    levels L        number of quantization levels (L = 2**bits)
    step  delta     (max - min) / L
    interval i      floor((x - min) / delta), clipped to 0 .. L-1
    quantized xq    min + (i + 0.5) * delta         (centre of the interval)
    error           xq - x                          (always within +-delta/2)
    code            i written in binary with `bits` digits
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .signal import Signal

MAX_BITS = 16          # 65536 levels is far more than a stem plot can show


def bits_to_levels(bits: int) -> int:
    """Number of levels available with `bits` bits: 2**bits."""
    if bits != int(bits) or not 1 <= bits <= MAX_BITS:
        raise ValueError(f"Number of bits must be a whole number from 1 to {MAX_BITS}.")
    return 2 ** int(bits)


def levels_to_bits(levels: int) -> int:
    """Bits needed to encode `levels` levels: ceil(log2(levels))."""
    if levels != int(levels) or not 2 <= levels <= 2 ** MAX_BITS:
        raise ValueError(f"Number of levels must be a whole number from 2 to {2 ** MAX_BITS}.")
    return (int(levels) - 1).bit_length()          # exact integer ceil(log2(levels))


@dataclass
class QuantizationResult:
    original: Signal
    quantized: Signal
    error: Signal                  # quantized - original
    levels: int
    bits: int
    step: float                    # interval width (delta)
    level_values: np.ndarray       # the L reconstruction values (interval mid-points)
    level_indices: np.ndarray      # interval number (0 .. L-1) of every sample
    codes: list[str]               # binary code of every sample


def quantize(signal: Signal, levels: int | None = None, bits: int | None = None
             ) -> QuantizationResult:
    """Quantize `signal` using either `levels` or `bits` (give exactly one).

    With bits, levels = 2**bits. With levels that are not a power of two, the
    code width is ceil(log2(levels)) bits.
    """
    if (levels is None) == (bits is None):
        raise ValueError("Give either the number of levels or the number of bits.")
    if len(signal) == 0:
        raise ValueError("The signal is empty.")
    if bits is not None:
        levels = bits_to_levels(bits)
    bits = levels_to_bits(levels)
    levels = int(levels)

    x = signal.values
    lo, hi = float(x.min()), float(x.max())
    step = (hi - lo) / levels

    if step == 0:                                   # constant signal: nothing to resolve
        idx = np.zeros(len(x), dtype=int)
    else:
        idx = np.clip(np.floor((x - lo) / step).astype(int), 0, levels - 1)

    level_values = lo + (np.arange(levels) + 0.5) * step
    xq = level_values[idx]

    quantized = Signal(signal.indices.copy(), xq, f"{signal.name}_quantized", fs=signal.fs)
    error = Signal(signal.indices.copy(), xq - x, f"{signal.name}_error", fs=signal.fs)
    codes = [format(int(i), f"0{bits}b") for i in idx]
    return QuantizationResult(signal, quantized, error, levels, bits, step,
                              level_values, idx, codes)
