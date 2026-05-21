# filename: ui/text_renderer.py
"""
Рендеринг текста с поддержкой кириллицы через Pillow.
OpenCV не умеет рисовать русские буквы — используем PIL.
"""
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

# Шрифты которые есть на Windows и поддерживают кириллицу
FONT_PATHS = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
]

_font_cache: dict = {}


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    if size in _font_cache:
        return _font_cache[size]
    for path in FONT_PATHS:
        try:
            font = ImageFont.truetype(path, size)
            _font_cache[size] = font
            return font
        except Exception:
            continue
    # Запасной вариант — встроенный шрифт PIL (без кириллицы, но не упадёт)
    font = ImageFont.load_default()
    _font_cache[size] = font
    return font


def put_text(frame: np.ndarray, text: str, pos: tuple,
             size: int = 24, color: tuple = (255, 255, 255),
             shadow: bool = True) -> np.ndarray:
    """
    Рисует текст с кириллицей на кадре OpenCV.
    color — в формате BGR (как в OpenCV).
    """
    # OpenCV использует BGR, PIL использует RGB
    rgb_color = (color[2], color[1], color[0])

    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw    = ImageDraw.Draw(img_pil)
    font    = _get_font(size)

    # Тень для читаемости
    if shadow:
        draw.text((pos[0] + 2, pos[1] + 2), text,
                  font=font, fill=(0, 0, 0))

    draw.text(pos, text, font=font, fill=rgb_color)

    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)