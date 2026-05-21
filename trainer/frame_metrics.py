# filename: trainer/frame_metrics.py
import math
from dataclasses import dataclass
from analysis.angles import calculate_angle, calculate_inclination

@dataclass
class FrameMetrics:
    knee_angle: int
    back_lean: int
    hip_ratio: float

    @classmethod
    def compute(cls, points: dict, camera_orientation: str = "lateral") -> "FrameMetrics":
        """
        Вычисляет биомеханические метрики для текущего кадра.
        """
        if not points or 'hip' not in points or 'knee' not in points:
            return cls(knee_angle=180, back_lean=0, hip_ratio=1.0)

        # 1. Угол колена (вычисляется по опорной/видимой стороне)
        knee_angle = calculate_angle(points['hip'], points['knee'], points['ankle'])

        # 2. Наклон спины с инвариантной геометрической формулой
        back_lean = calculate_inclination(points['shoulder'], points['hip'])

        # 3. Высота таза (нормализованная глубина приседа)
        if camera_orientation == "frontal":
            # Во фронтальном режиме берем усредненные билатеральные параметры ног
            shin_l = math.hypot(points['knee_l'][0] - points['ankle_l'][0], points['knee_l'][1] - points['ankle_l'][1]) if 'knee_l' in points else 10.0
            shin_r = math.hypot(points['knee_r'][0] - points['ankle_r'][0], points['knee_r'][1] - points['ankle_r'][1]) if 'knee_r' in points else 10.0
            shin_length = max((shin_l + shin_r) / 2.0, 10.0)

            hip_y = (points['hip_l'][1] + points['hip_r'][1]) / 2.0 if 'hip_l' in points else points['hip'][1]
            knee_y = (points['knee_l'][1] + points['knee_r'][1]) / 2.0 if 'knee_l' in points else points['knee'][1]

            hip_ratio = (knee_y - hip_y) / shin_length
        else:
            # В боковом режиме используем длину бедра опорной стороны
            hip, knee = points['hip'], points['knee']
            thigh_length = max(math.hypot(knee[0] - hip[0], knee[1] - hip[1]), 10.0)
            hip_ratio = (knee[1] - hip[1]) / thigh_length

        return cls(knee_angle=knee_angle, back_lean=back_lean, hip_ratio=hip_ratio)
