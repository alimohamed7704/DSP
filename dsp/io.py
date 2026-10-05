from __future__ import annotations
from pathlib import Path
from .signal import Signal


def read_signal(path) -> Signal:
    path = Path(path)
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    if not lines:
        raise ValueError("File is empty")
    try:
        n = int(float(lines[0]))
    except ValueError:
        raise ValueError("First row must be the number of samples N")

    rows = lines[1:]
    if len(rows) != n:
        raise ValueError(f"Header says N={n} but file has {len(rows)} sample rows")

    idx, val = [], []
    for i, row in enumerate(rows, start=2):
        parts = row.replace(",", " ").split()
        if len(parts) != 2:
            raise ValueError(f"Line {i}: expected 'index value', got '{row}'")
        idx.append(int(float(parts[0])))
        val.append(float(parts[1]))
    return Signal(idx, val, name=path.stem)


def write_signal(signal: Signal, path) -> None:
    out = [str(len(signal))]
    out += [f"{i} {v:g}" for i, v in zip(signal.indices, signal.values)]
    Path(path).write_text("\n".join(out) + "\n")