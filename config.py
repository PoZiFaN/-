# filename: config.py
import cv2
import logging
import os
import platform

os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AITrainer.Config")

# Системные настройки (АДАПТИРОВАНО ПОД AMD RYZEN 5 3500U)
TARGET_FPS = 15  # Снижено до 15 FPS для стабильной работы на CPU без лагов
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Режимы ракурса съемки
ORIENTATION_LATERAL = "lateral"  # Сбоку (90°)
ORIENTATION_FRONTAL = "frontal"  # Спереди (0°)

# Основные настройки упражнения
SQUAT_DEPTH, RESET_ANGLE   = 110, 160
WARN_OFFSET, BAD_OFFSET    = 30, 45

# Калибровка увеличена до 7.0 секунд (105 кадров при 15 FPS)
# Это дает спортсмену достаточно времени, чтобы занять исходное положение и зафиксировать стойку.
CALIBRATION_FRAMES         = int(TARGET_FPS * 7.0)  
DEBOUNCE_FRAMES            = 2  # Уменьшено из-за низкого FPS
ERROR_DEBOUNCE_FRAMES      = 2  # Базовый антидребезг

# Настройки времени фаз (в секундах)
MIN_DESCENT_TIME = 0.5  # Порог слишком быстрого спуска

# Границы для спинбоксов в GUI
SQUAT_DEPTH_MIN, SQUAT_DEPTH_MAX = 80,  130
RESET_ANGLE_MIN, RESET_ANGLE_MAX = 140, 175
WARN_OFFSET_MIN, WARN_OFFSET_MAX = 10,  60
BAD_OFFSET_MIN,  BAD_OFFSET_MAX  = 20,  80

# Пороги для колена (в долях от длины голени)
KNEE_TOE_RATIO_WARN = 0.60
KNEE_TOE_RATIO_BAD  = 0.90

# Тайминги скорости (адаптированы под TARGET_FPS = 15)
MIN_DESCENT_FRAMES  = 10   # Минимум ~0.66 сек на спуск
MIN_ASCENT_FRAMES   = 5    # Минимум ~0.33 сек на подъем
STABILITY_BUFFER_SIZE = 15
STABILITY_THRESHOLD   = 25 # Допуск на дрожание коленей

# Асимметрия и Вальгус
FRONTAL_SHOULDER_DIFF  = 60
LATERAL_SHOULDER_DIFF  = 120
VALGUS_WARN_RATIO = 0.10
VALGUS_BAD_RATIO  = 0.22

# Цвета (BGR для OpenCV)
GREEN     = (0, 255, 0)
YELLOW    = (0, 255, 255)
RED       = (0, 0, 255)
WHITE     = (255, 255, 255)
DARK_GRAY = (40, 40, 40)
CYAN      = (255, 200, 0)

_DETECTED_CAMERA_ID = None

def get_camera_id() -> int:
    """
    Возвращает индекс активной камеры.
    Реализует безопасную кроссплатформенную инициализацию девайса.
    """
    global _DETECTED_CAMERA_ID
    if _DETECTED_CAMERA_ID is not None:
        return _DETECTED_CAMERA_ID
    for idx in range(5):
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            cap.release()
            _DETECTED_CAMERA_ID = idx
            return idx
    _DETECTED_CAMERA_ID = 0
    return 0
