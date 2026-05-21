# filename: analysis/lateral_checks.py
"""Проверки наклона спины и колена — работают при съёмке под 45°."""
import math
import config
from analysis.angles import calculate_inclination


def check_back_lean(points: dict, baseline: int) -> tuple[str, str]:
    """
    Проверяет наклон спины относительно калиброванного базового значения.
    """
    current_lean = calculate_inclination(points['shoulder'], points['hip'])
    delta = current_lean - baseline

    # Сравнение с конфигурационными допусками отклонений
    if delta > config.BAD_OFFSET:
        return "СЛИШКОМ СИЛЬНЫЙ НАКЛОН!", "BAD"
    if delta > config.WARN_OFFSET:
        return "ДЕРЖИ СПИНУ ПРЯМО", "WARNING"

    return "", ""


def check_knee_over_toe(points: dict) -> tuple[str, str]:
    """
    Колено не должно уходить слишком далеко вперёд носка.
    Использует длину голени (shin) в качестве биомеханического калибратора,
    а также учитывает анатомическое направление взгляда пользователя.
    """
    knee_x, knee_y = points['knee']
    ankle_x, ankle_y = points['ankle']
    hip_x, _ = points['hip']

    # Вычисляем реальную длину голени в пикселях
    shin_length = math.hypot(knee_x - ankle_x, knee_y - ankle_y)
    shin_length = max(shin_length, 10.0)

    # Вычисляем анатомическое направление взгляда: 1, если лицом вправо, -1 если влево
    facing_dir = 1.0 if knee_x >= hip_x else -1.0

    # Насколько колено ушло вперед лодыжки с учетом направления
    overshoot = (knee_x - ankle_x) * facing_dir / shin_length

    # Отрегулированные биомеханические пороги (сбалансированные):
    # 0.48 — колено начинает выходить за физиологический предел для компенсации длины бедра (Warning)
    # 0.58 — критический завал веса на носки (Bad)
    if overshoot > 0.58:
        return "КОЛЕНО СЛИШКОМ ВПЕРЁД!", "BAD"
    if overshoot > 0.48:
        return "СЛЕДИ ЗА КОЛЕНОМ", "WARNING"
    return "", ""


def check_lumbar_bounce(back_lean_history: list, phase: str) -> tuple[str, str]:
    """
    Детектирует двойное движение в поясничном отделе (нестабильный наклон спины / Butt Wink).
    Происходит, когда наклон спины совершает колебательные движения во время спуска.
    Использует скользящее среднее для подавления шума детектора.
    """
    if len(back_lean_history) < 15 or phase != "descending":
        return "", ""

    # Сглаживаем скользящим средним размером 3 для подавления джиттера нейросети
    history = back_lean_history[-15:]
    smoothed = []
    for i in range(1, len(history) - 1):
        val = (history[i-1] + history[i] + history[i+1]) / 3.0
        smoothed.append(val)

    # Находим разности между сглаженными значениями
    diffs = [smoothed[i] - smoothed[i-1] for i in range(1, len(smoothed))]

    # Подсчитываем выраженные изменения направления движения
    sign_changes = 0
    prev_sign = 0
    for d in diffs:
        if abs(d) < 1.5:  # Фильтр выраженных изменений (>1.5 градусов за кадр)
            continue
        curr_sign = 1 if d > 0 else -1
        if prev_sign != 0 and curr_sign != prev_sign:
            sign_changes += 1
        prev_sign = curr_sign

    # Только если зафиксировано реальное многократное раскачивание поясницы
    if sign_changes >= 2:
        return "ДВОЙНОЕ ДВИЖЕНИЕ ПОЯСНИЦЕЙ!", "WARNING"

    return "", ""


def check_hip_drive_error(back_lean_history: list, knee_angle_history: list, phase: str, baseline: int) -> tuple[str, str]:
    """
    Детектирует ошибку резкого подъема таза относительно спины (Good Morning Squat).
    Происходит, когда в фазе подъема таз (зад) поднимается быстрее плечевого пояса,
    после чего спина резко 'догоняет' движение.
    """
    if len(back_lean_history) < 6 or len(knee_angle_history) < 6 or phase != "ascending":
        return "", ""

    curr_back = back_lean_history[-1]
    prev_back = back_lean_history[-2]

    curr_knee = knee_angle_history[-1]
    prev_knee = knee_angle_history[-2]

    delta_back = curr_back - prev_back
    delta_knee = curr_knee - prev_knee

    # Скорость выпрямления спины (prev_back - curr_back)
    straightening_speed = prev_back - curr_back

    # Случай 1: Разгибаем колени (встаем), но наклон спины увеличивается (таз ушел вверх, спина завалилась вперед)
    if delta_knee > 2.0 and delta_back > 1.0 and curr_back > (baseline + 15):
        return "ТАЗ ПОДНИМАЕТСЯ БЫСТРЕЕ СПИНЫ!", "WARNING"

    # Случай 2: Резкий рывок спиной вверх после завала (straightening_speed больше 4 градусов за кадр)
    if straightening_speed > 4.0 and curr_knee > 120:
        return "РЕЗКИЙ ПОДЪЁМ СПИНЫ С ТАЗОМ!", "BAD"

    return "", ""
