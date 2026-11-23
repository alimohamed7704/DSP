from __future__ import annotations
import numpy as np
from .signal import Signal, WaveParams

KINDS = ("sine", "cosine")
MAX_SAMPLES = 5000     # keeps the stem plot readable and fast


def nyquist_rate(frequency: float) -> float:
    """Minimum sampling frequency allowed by the sampling theorem: 2 * f."""
    return 2.0 * frequency


def check_sampling_theorem(frequency: float, sampling_frequency: float) -> None:
    """Raise ValueError if fs < 2f (the sampling theorem is violated)."""
    if sampling_frequency < nyquist_rate(frequency):
        raise ValueError(
            f"Sampling theorem violated: fs must be at least 2*f = "
            f"{nyquist_rate(frequency):g} Hz, but fs = {sampling_frequency:g} Hz.")


def generate_wave(kind: str, amplitude: float, frequency: float,
                  sampling_frequency: float, phase: float = 0.0,
                  duration: float = 1.0, name: str | None = None) -> Signal:
    """Generate x(n) = A * sin/cos(2*pi*f*n/fs + phase), n = 0 .. N-1.

    kind                -- "sine" or "cosine"
    amplitude           -- A
    frequency           -- analog frequency f in Hz (>= 0)
    sampling_frequency  -- fs in Hz, must satisfy fs >= 2f
    phase               -- theta in radians
    duration            -- length of the signal in seconds, N = round(duration * fs)
    """
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    if frequency < 0:
        raise ValueError("Analog frequency must be >= 0 Hz.")
    if sampling_frequency <= 0:
        raise ValueError("Sampling frequency must be > 0 Hz.")
    if duration <= 0:
        raise ValueError("Duration must be > 0 seconds.")
    check_sampling_theorem(frequency, sampling_frequency)

    n_samples = int(round(duration * sampling_frequency))
    if n_samples < 2:
        raise ValueError("Duration is too short: the signal would have fewer than 2 samples.")
    if n_samples > MAX_SAMPLES:
        raise ValueError(
            f"Too many samples ({n_samples}). Reduce the duration or the sampling "
            f"frequency (maximum is {MAX_SAMPLES} samples).")

    wave = WaveParams(kind, float(amplitude), float(frequency),
                      float(sampling_frequency), float(phase))
    n = np.arange(n_samples)
    if name is None:
        name = (f"{kind}(A={amplitude:g}, f={frequency:g}Hz, "
                f"fs={sampling_frequency:g}Hz, th={phase:.3g}rad)")
    return Signal(n, wave.evaluate(n), name=name, wave=wave)
