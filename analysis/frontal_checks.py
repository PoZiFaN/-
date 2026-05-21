# filename: analysis/frontal_checks.py
"""
Проверка вальгуса и асимметрии при съёмке спереди или под 45°.
Реализует математически точные, масштабно-инвариантные биомеханические метрики.
"""
import math
import config


def check_valgus(points: dict) -> tuple[str, str]:
    """
    Масштабно-инвариантный и перспективно-компенсированный анализ вальгуса.
    Сравнивает горизонтальное расстояние между коленями с расстоянием между лодыжками.
    """
    confs = [
        points.get('knee_l_conf', 0), points.get('knee_r_conf', 0),
        points.get('ankle_l_conf', 0), points.get('ankle_r_conf', 0)
    ]

    # Если хоть одна точка перекрыта (уверенность < 65%), отменяем проверку
    if any(c < 0.65 for c in confs):
        return "", ""

    ankle_dist = abs(points['ankle_l'][0] - points['ankle_r'][0])
    knee_dist = abs(points['knee_l'][0] - points['knee_r'][0])

    # Защита: если человек стоит почти боком, лодыжки визуально сливаются
    if ankle_dist < 20.0:
        return "", ""

    # Соотношение ширины коленей к ширине лодыжек
    ratio = knee_dist / ankle_dist

    # Скорректированные биомеханические пороги для 2D-проекции:
    # Нормальный присед: колени на ширине стоп или шире (ratio >= 0.95)
    # Завал внутрь (вальгус): ratio падает ниже 0.85 (предупреждение), ниже 0.72 (опасный завал)
    if ratio < 0.72:
        return "КОЛЕНИ ВНУТРЬ — ОПАСНО!", "BAD"
    if ratio < 0.85:
        return "РАЗВОДИ КОЛЕНИ ШИРЕ", "WARNING"

    return "", ""


def check_symmetry(points: dict) -> tuple[str, str]:
    """
    Анализ асимметрии глубины седа между левой и правой ногами.
    Измеряет разность вертикальных сжатий тазобедренного сектора,
    нормализованную по средней длине голени для компенсации наклонов камеры.
    """
    confs = [
        points.get('knee_l_conf', 0), points.get('knee_r_conf', 0),
        points.get('hip_l_conf', 0), points.get('hip_r_conf', 0),
        points.get('ankle_l_conf', 0), points.get('ankle_r_conf', 0)
    ]
    if any(c < 0.65 for c in confs):
        return "", ""

    # Считаем длины голеней для калибровки масштаба
    shin_l = math.hypot(points['knee_l'][0] - points['ankle_l'][0], points['knee_l'][1] - points['ankle_l'][1])
    shin_r = math.hypot(points['knee_r'][0] - points['ankle_r'][0], points['knee_r'][1] - points['ankle_r'][1])
    avg_shin = max((shin_l + shin_r) / 2.0, 10.0)

    # Вычисляем вертикальные расстояния (проекции бедер по высоте)
    depth_l = points['knee_l'][1] - points['hip_l'][1]
    depth_r = points['knee_r'][1] - points['hip_r'][1]

    # Относительная асимметрия
    asymmetry = abs(depth_l - depth_r) / avg_shin

    # Повышаем чувствительность: порог 15% указывает на заметный перекос таза
    if asymmetry > 0.15:
        if depth_l > depth_r:
            return "НЕРАВНОМЕРНЫЙ ПРИСЕД (ПЕРЕКОС ВПРАВО)", "WARNING"
        else:
            return "НЕРАВНОМЕРНЫЙ ПРИСЕД (ПЕРЕКОС ВЛЕВО)", "WARNING"

    return "", ""
