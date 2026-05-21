# filename: ui/hud.py
import cv2
import config
from ui.text_renderer import put_text


def draw_training_hud(frame, counter, target, feedback, color, state):
    """
    Отрисовывает статус-бар тренировки.
    Фокусируется на качестве выполнения движения и корректности осанки.
    """
    cv2.rectangle(frame, (0, 0), (420, 150), config.DARK_GRAY, -1)

    frame = put_text(frame, f"ПОВТОРЫ: {counter} / {target}",
                     (15, 10), size=32, color=config.WHITE)
    
    # Текст фокус-подсказки по положению звеньев тела
    frame = put_text(frame, feedback,
                     (15, 60), size=26, color=color)

    state_text  = "ВНИЗ ↓" if state == "DOWN" else "ВВЕРХ ↑"
    state_color = config.GREEN if state == "DOWN" else config.WHITE
    frame = put_text(frame, state_text,
                     (15, 108), size=22, color=state_color)
    return frame


def draw_calibration_bar(frame, calib_frames):
    h, w = frame.shape[:2]
    bar_w    = w - 200
    progress = int((calib_frames / config.CALIBRATION_FRAMES) * bar_w)

    cv2.rectangle(frame, (100, h//2),
                  (100+bar_w, h//2+30), config.DARK_GRAY, -1)
    cv2.rectangle(frame, (100, h//2),
                  (100+progress, h//2+30), config.GREEN, -1)
    cv2.rectangle(frame, (100, h//2),
                  (100+bar_w, h//2+30), config.WHITE, 2)

    frame = put_text(frame, "ВСТАНЬ ПРЯМО И НЕ ДВИГАЙСЯ...",
                     (w//2 - 220, h//2 - 40), size=26, color=config.WHITE)
    return frame
