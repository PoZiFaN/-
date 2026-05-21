# filename: ui/orientation_prompt.py
import config
from ui.text_renderer import put_text


def draw_position_hint(frame, camera_orientation="lateral"):
    """Отрисовывает требования к углу съемки."""
    h, w = frame.shape[:2]
    text = "КАМЕРА: 90° СБОКУ" if camera_orientation == config.ORIENTATION_LATERAL else "КАМЕРА: 0° СПЕРЕДИ"
    frame = put_text(frame, text,
                     (w - 260, h - 45), size=20, color=config.CYAN)
    return frame
