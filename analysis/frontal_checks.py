# filename: analysis/frontal_checks.py
"""
Проверка вальгуса при съёмке под 45°.
Учитывает перспективное искажение 2D-камеры.
"""
import config


def check_valgus(points: dict) -> tuple[str, str]:
    """
    Умная проверка вальгуса с поправкой на перспективу.
    """
    # 1. Проверяем, уверена ли нейросеть в положении обеих ног
    confs = [
        points.get('knee_l_conf', 0), points.get('knee_r_conf', 0),
        points.get('ankle_l_conf', 0), points.get('ankle_r_conf', 0)
    ]

    # Если хоть одна точка перекрыта (уверенность < 65%), отменяем проверку
    if any(c < 0.65 for c in confs):
        return "", ""

    # 2. 2D расстояния на экране
    ankle_dist = abs(points['ankle_l'][0] - points['ankle_r'][0])
    knee_dist = abs(points['knee_l'][0] - points['knee_r'][0])

    # Защита: если человек стоит почти боком (чистый профиль),
    # лодыжки визуально сливаются в одну точку. В таком ракурсе вальгус не меряем.
    if ankle_dist < 20.0:
        return "", ""

    # Соотношение ширины коленей к ширине стоп
    ratio = knee_dist / ankle_dist

    # 3. Применяем пороги из config.py (а не жестко заданные цифры)
    # При 45° колени могут визуально почти накладываться друг на друга,
    # поэтому мы штрафуем только за жесткое перекрытие.
    severe_threshold = min(config.VALGUS_WARN_RATIO, config.VALGUS_BAD_RATIO) # 0.10
    warn_threshold   = max(config.VALGUS_WARN_RATIO, config.VALGUS_BAD_RATIO) # 0.22

    if ratio < severe_threshold:
        return "КОЛЕНИ ВНУТРЬ — ОПАСНО!", "BAD"
    if ratio < warn_threshold:
        return "РАЗВОДИ КОЛЕНИ ШИРЕ", "WARNING"

    return "", ""


def check_symmetry(points: dict) -> tuple[str, str]:
    """
    Асимметрия: одна нога приседает меньше другой.
    Адаптировано под перспективное искажение камеры под углом 45 градусов.
    """
    confs = [points.get('knee_l_conf', 0), points.get('knee_r_conf', 0)]
    if any(c < 0.65 for c in confs):
        return "", ""

    # Защита от джиттера: если разница уверенностей детекции суставов > 0.2, пропускаем этот кадр
    if abs(points.get('knee_l_conf', 0) - points.get('knee_r_conf', 0)) > 0.2:
        return "", ""

    knee_l_y = points['knee_l'][1]
    knee_r_y = points['knee_r'][1]
    diff = abs(knee_l_y - knee_r_y)

    ankle_dist = abs(points['ankle_l'][0] - points['ankle_r'][0])
    stance = max(ankle_dist, 30.0)

    # Порог увеличен с 0.20 до 0.35 для компенсации ракурса камеры 45°
    if diff / stance > 0.35:
        return "НЕРАВНОМЕРНОЕ ПРИСЕДАНИЕ!", "WARNING"
    return "", ""
