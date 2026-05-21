# filename: core/smoother.py
import math
from typing import List

# Добавлены левое и правое плечо для корректного сглаживания во фронтальном режиме
BILATERAL_KEYS = [
    "knee_l", "knee_r", "ankle_l", "ankle_r", 
    "hip_l", "hip_r", "shoulder_l", "shoulder_r"
]
MAIN_KEYS = ["shoulder", "hip", "knee", "ankle"]


class OneEuroFilter:
    """Адаптивный фильтр 1Euro для координат x, y."""

    def __init__(self, min_cutoff: float = 0.5, beta: float = 0.02, d_cutoff: float = 1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = None
        self.dx_prev = None

    def _alpha(self, cutoff: float, dt: float) -> float:
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def __call__(self, x: List[int], dt: float = 0.033) -> List[int]:
        if self.x_prev is None:
            self.x_prev = [float(v) for v in x]
            self.dx_prev = [0.0 for _ in x]
            return x

        dx = [(x[i] - self.x_prev[i]) / dt for i in range(len(x))]
        alpha_d = self._alpha(self.d_cutoff, dt)
        edx = [alpha_d * dx[i] + (1.0 - alpha_d) * self.dx_prev[i] for i in range(len(x))]

        speed = math.sqrt(sum(v * v for v in edx))
        cutoff = self.min_cutoff + self.beta * speed

        alpha = self._alpha(cutoff, dt)
        x_hat = [alpha * x[i] + (1.0 - alpha) * self.x_prev[i] for i in range(len(x))]

        self.x_prev = x_hat
        self.dx_prev = edx
        return [int(x_hat[0]), int(x_hat[1])]


class PoseSmoother:
    def __init__(self):
        self.filters: dict = {}
        self.reset()

    def reset(self):
        self.filters = {
            key: OneEuroFilter(min_cutoff=0.5, beta=0.02)
            for key in MAIN_KEYS + BILATERAL_KEYS
        }

    def smooth(self, current: dict) -> dict:
        result = {}
        # Сначала копируем ВСЕ ключи (включая показатели уверенности _conf)
        for k, v in current.items():
            result[k] = v

        # Затем перезаписываем координаты сглаженными значениями
        for joint in MAIN_KEYS + BILATERAL_KEYS:
            if joint in current:
                result[joint] = self.filters[joint](current[joint])

        return result
