from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class Signal:
    """A discrete signal: integer sample indices and their values."""
    indices: np.ndarray
    values: np.ndarray
    name: str = "signal"

    def __post_init__(self):
        self.indices = np.asarray(self.indices, dtype=int)
        self.values = np.asarray(self.values, dtype=float)
        if self.indices.shape != self.values.shape:
            raise ValueError("indices and values must have the same length")
        order = np.argsort(self.indices, kind="stable")   # keep sorted by n
        self.indices = self.indices[order]
        self.values = self.values[order]

    def __len__(self) -> int:
        return len(self.indices)