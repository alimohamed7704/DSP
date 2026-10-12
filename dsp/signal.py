from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass(frozen=True)
class WaveParams:
    """Analytic description of a generated sine / cosine wave.

    x(n) = A * trig(2*pi*f*n/fs + phase)      (phase in radians)

    Kept on the Signal so it can be drawn as a true continuous waveform
    (the analog signal x(t) the samples were taken from).
    """
    kind: str            # "sine" or "cosine"
    amplitude: float
    frequency: float     # analog frequency f (Hz)
    sampling_frequency: float   # fs (Hz)
    phase: float         # theta (radians)

    def evaluate(self, n) -> np.ndarray:
        """Evaluate the wave at (possibly fractional) sample positions n."""
        trig = np.sin if self.kind == "sine" else np.cos
        n = np.asarray(n, dtype=float)
        return self.amplitude * trig(
            2 * np.pi * self.frequency * n / self.sampling_frequency + self.phase)


@dataclass
class Signal:
    """A discrete signal: integer sample indices and their values."""
    indices: np.ndarray
    values: np.ndarray
    name: str = "signal"
    wave: Optional[WaveParams] = None   # set only for generated sine/cosine signals
    fs: Optional[float] = None          # sampling frequency in Hz (None = unknown)

    def __post_init__(self):
        self.indices = np.asarray(self.indices, dtype=int)
        self.values = np.asarray(self.values, dtype=float)
        if self.fs is None and self.wave is not None:
            self.fs = self.wave.sampling_frequency      # generated waves already know fs
        if self.fs is not None and self.fs <= 0:
            raise ValueError("Sampling frequency must be > 0")
        if self.indices.shape != self.values.shape:
            raise ValueError("indices and values must have the same length")
        order = np.argsort(self.indices, kind="stable")   # keep sorted by n
        self.indices = self.indices[order]
        self.values = self.values[order]

    def __len__(self) -> int:
        return len(self.indices)

    def time_axis(self, n=None) -> np.ndarray:
        """Convert sample positions to seconds: t = n / fs (default: this signal's indices)."""
        if self.fs is None:
            raise ValueError(f"'{self.name}' has no sampling frequency")
        return np.asarray(self.indices if n is None else n, dtype=float) / self.fs

    def continuous(self, points_per_sample: int = 20):
        """Return (x, y) for drawing the signal as a continuous curve.

        * Generated sine/cosine signals: the exact analog waveform, densely
          evaluated between the first and last sample.
        * Any other signal (loaded from file, result of an operation): the
          samples joined by straight lines.
        """
        if self.wave is None or len(self) < 2:
            return self.indices.astype(float), self.values
        num = int(min(max(len(self) * points_per_sample, 500), 20000))
        n = np.linspace(self.indices[0], self.indices[-1], num)
        return n, self.wave.evaluate(n)
