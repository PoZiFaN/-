# filename: ui/overlay.py
"""AR-метрики прямо на теле."""
import cv2
import config
from ui.text_renderer import put_text
from analysis.angles import calculate_angle


def draw_skeleton(frame, points, color, camera_orientation="lateral"):
    if camera_orientation == config.ORIENTATION_FRONTAL:
        # Во фронтальном ракурсе (спереди) отрисовываем обе ноги и связующие линии
        connections = [
            ("shoulder_l", "hip_l"), ("hip_l", "knee_l"), ("knee_l", "ankle_l"),
            ("shoulder_r", "hip_r"), ("hip_r", "knee_r"), ("knee_r", "ankle_r")
        ]
        for a, b in connections:
            if a in points and b in points:
                cv2.line(frame, tuple(points[a]), tuple(points[b]), color, 4)

        # Рисуем поперечные линии для наглядного контроля симметрии
        cross_connections = [
            ("shoulder_l", "shoulder_r"),
            ("hip_l", "hip_r"),
            ("knee_l", "knee_r")
        ]
        for a, b in cross_connections:
            if a in points and b in points:
                cv2.line(frame, tuple(points[a]), tuple(points[b]), config.CYAN, 2)

        # Отрисовываем все ключевые суставы обеих сторон
        joints = [
            "shoulder_l", "shoulder_r",
            "hip_l", "hip_r",
            "knee_l", "knee_r",
            "ankle_l", "ankle_r"
        ]
        for key in joints:
            if key in points and isinstance(points[key], (list, tuple)) and len(points[key]) >= 2:
                cv2.circle(frame, tuple(points[key][:2]), 8, color, -1)
    else:
        # Классический ракурс сбоку (90 градусов) — рисуем только одну доминирующую сторону
        for a, b in [("hip", "knee"), ("knee", "ankle"), ("shoulder", "hip")]:
            if a in points and b in points:
                cv2.line(frame, tuple(points[a]), tuple(points[b]), color, 4)

        for key, pt in points.items():
            # Пропускаем служебные данные и билатеральные суставы в режиме сбоку
            if key == "side" or key.endswith("_conf") or key in (
                    "knee_l", "knee_r", "ankle_l", "ankle_r", "hip_l", "hip_r", "shoulder_l", "shoulder_r"
            ):
                continue

            if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                cv2.circle(frame, tuple(pt[:2]), 8, color, -1)


def draw_metrics(frame, points, knee_angle, back_lean, back_color, camera_orientation="lateral"):
    """
    Отрисовывает биомеханические метрики в зависимости от выбранного ракурса.
    """
    if camera_orientation == config.ORIENTATION_LATERAL:
        kx, ky = points['knee']
        frame = put_text(frame, f"{knee_angle}°",
                         (kx + 15, ky - 15), size=22, color=config.WHITE)

        mx = int((points['shoulder'][0] + points['hip'][0]) / 2) + 15
        my = int((points['shoulder'][1] + points['hip'][1]) / 2)
        frame = put_text(frame, f"Наклон: {back_lean}°",
                         (mx, my), size=20, color=back_color)
    else:
        # Во фронтальном режиме вычисляем и выводим углы для ОБЕИХ ног независимо
        if "hip_l" in points and "knee_l" in points and "ankle_l" in points:
            l_angle = calculate_angle(points["hip_l"], points["knee_l"], points["ankle_l"])
            kl_x, kl_y = points['knee_l']
            frame = put_text(frame, f"L: {l_angle}°",
                             (kl_x - 75, kl_y - 15), size=20, color=config.WHITE)

        if "hip_r" in points and "knee_r" in points and "ankle_r" in points:
            r_angle = calculate_angle(points["hip_r"], points["knee_r"], points["ankle_r"])
            kr_x, kr_y = points['knee_r']
            frame = put_text(frame, f"R: {r_angle}°",
                             (kr_x + 15, kr_y - 15), size=20, color=config.WHITE)

        # Отрисовываем горизонтальные соединительные оси для визуального контроля симметрии
        if "knee_l" in points and "knee_r" in points:
            cv2.line(frame, tuple(points["knee_l"]), tuple(points["knee_r"]), config.CYAN, 2)
        if "hip_l" in points and "hip_r" in points:
            cv2.line(frame, tuple(points["hip_l"]), tuple(points["hip_r"]), config.CYAN, 2)

    side = points.get("side", "")
    if side:
        sx, sy = points['shoulder']
        label = "ЛЕВО" if side == "left" else "ПРАВО"
        frame = put_text(frame, label,
                         (sx - 60, sy - 30), size=18, color=config.YELLOW)
    return frame
