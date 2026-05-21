# filename: analysis/angles.py
import numpy as np
from typing import Union, Tuple

Point = Union[Tuple[int, int], list, np.ndarray]


def calculate_angle(a: Point, b: Point, c: Point) -> int:
    """Угол ABC в точке B."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    n_ba, n_bc = np.linalg.norm(ba), np.linalg.norm(bc)
    if n_ba == 0 or n_bc == 0:
        return 0
    cos = np.clip(np.dot(ba, bc) / (n_ba * n_bc), -1.0, 1.0)
    return int(np.degrees(np.arccos(cos)))


def calculate_inclination(p1: Point, p2: Point, knee_x: float = None, hip_x: float = None) -> int:
    """
    Вычисляет угол наклона отрезка p1-p2 относительно вертикали.
    Использует абсолютное горизонтальное смещение, что делает расчет
    полностью инвариантным к направлению взгляда (влево/вправо).
    p1 - плечо, p2 - таз.
    """
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    if dy == 0:
        return 90
    return int(np.degrees(np.arctan(dx / dy)))
