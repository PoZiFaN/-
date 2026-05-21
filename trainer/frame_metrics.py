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
    def compute(cls, points: dict) -> "FrameMetrics":
        if not points or 'hip' not in points or 'knee' not in points:
            return cls(knee_angle=180, back_lean=0, hip_ratio=1.0)

        # 1. Угол колена
        knee_angle = calculate_angle(points['hip'], points['knee'], points['ankle'])

        # 2. Наклон спины с учетом СТОРОНЫ тела (side)
        side = points.get("side", "right")
        back_lean = calculate_inclination(points['shoulder'], points['hip'], side)

        # 3. Высота таза
        hip, knee = points['hip'], points['knee']
        thigh_length = max(math.hypot(knee[0] - hip[0], knee[1] - hip[1]), 10.0)
        hip_ratio = (knee[1] - hip[1]) / thigh_length

        return cls(knee_angle=knee_angle, back_lean=back_lean, hip_ratio=hip_ratio)