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
        # Полностью отключено по требованию пользователя во избежание раздражающих подсказок
        return "", ""
