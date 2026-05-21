# filename: analysis/lateral_checks.py
"""Проверки наклона спины и колена — работают при съёмке под 45°."""
import math
import config
from analysis.angles import calculate_inclination


def check_back_lean(points: dict, baseline: int) -> tuple[str, str]:
    """
    Проверяет наклон спины относительно калиброванного базового значения.
    При 45° калибровка автоматически компенсирует угол камеры.
    """
    # Вычисляем текущий наклон от вертикали (в градусах)
    current_lean = calculate_inclination(points['shoulder'], points['hip'])

    # Разница между тем как стоим сейчас и как стояли при калибровке
    delta = current_lean - baseline

    # Если наклон стал слишком большим
    if delta > config.BAD_OFFSET:
        return "СЛИШКОМ СИЛЬНЫЙ НАКЛОН!", "BAD"
    if delta > config.WARN_OFFSET:
        return "ДЕРЖИ СПИНУ ПРЯМО", "WARNING"

    # Если наклон в норме
    return "", ""


def check_knee_over_toe(points: dict) -> tuple[str, str]:
    """
    Колено не должно уходить слишком далеко вперёд носка.
    Используем длину голени (shin) как "биомеханическую линейку".
    """
    knee_x, knee_y = points['knee']
    ankle_x, ankle_y = points['ankle']

    # Вычисляем реальную длину голени в пикселях
    shin_length = math.hypot(knee_x - ankle_x, knee_y - ankle_y)
    shin_length = max(shin_length, 10.0)

    # Насколько колено ушло вперед лодыжки (в долях от длины голени)
    overshoot = (knee_x - ankle_x) / shin_length

    if overshoot > config.KNEE_TOE_RATIO_BAD:
        return "КОЛЕНО СЛИШКОМ ВПЕРЁД!", "BAD"
    if overshoot > config.KNEE_TOE_RATIO_WARN:
        return "СЛЕДИ ЗА КОЛЕНОМ", "WARNING"
    return "", ""