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


def calculate_inclination(p1: Point, p2: Point, side: str = "right") -> int:
    """
    Угол наклона отрезка p1-p2 относительно вертикали.
    Учитывает сторону тела, чтобы наклон ВПЕРЕД всегда был положительным.
    p1 - плечо, p2 - таз.
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]  # В OpenCV Y растет вниз, поэтому dy обычно отрицательный

    # Если стоим левым боком, инвертируем X, чтобы наклон вперед (влево)
    # давал такой же результат, как наклон вправо.
    if side == "left":
        dx = -dx

    # Мы используем arctan2(dx, dy), где dy берем по модулю,
    # чтобы мерить отклонение от вертикальной оси.
    return int(np.degrees(np.arctan2(dx, abs(dy))))