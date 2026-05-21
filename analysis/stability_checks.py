# filename: analysis/stability_checks.py
"""Стабильность в нижней точке приседания."""
import numpy as np
import config


class StabilityTracker:
    def __init__(self):
        self._buf: list = []

    def reset(self):
        self._buf = []

    def update(self, points: dict, state: str):
        if state == "DOWN":
            self._buf.append(points['knee'][:])
            if len(self._buf) > config.STABILITY_BUFFER_SIZE:
                self._buf.pop(0)
        else:
            self.reset()

    def check(self) -> tuple[str, str]:
        if len(self._buf) < 5:
            return "", ""
        arr = np.array(self._buf)
        std = float(np.std(arr))
        if std > config.STABILITY_THRESHOLD:
            return "HOLD STEADY!", "WARNING"
        return "", ""