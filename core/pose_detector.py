# filename: core/pose_detector.py
import torch
import logging
import numpy as np
from ultralytics import YOLO
from core.smoother import PoseSmoother
from core.side_detector import get_best_side, get_side_indices
from core.camera_orientation import detect_orientation

logger = logging.getLogger("AITrainer.Pose")

# Оптимизация PyTorch под 4-ядерный процессор (снижает нагрузку на ОЗУ и ЦП)
torch.set_num_threads(4)


class PoseDetector:
    def __init__(self, model_path='yolov8n-pose.pt'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        # Жестко ставим 320 для CPU. Выше - будут лаги, ниже - нейросеть ослепнет.
        self.imgsz = 640 if self.device == 'cuda' else 320
        self.model = YOLO(model_path)
        self.model.to(self.device)
        self.smoother = PoseSmoother()
        self.orientation = "unknown"
        logger.info(f"Pose: device={self.device}, imgsz={self.imgsz}")

    def find_pose(self, frame) -> dict | None:
        """
        Обнаруживает ключевые точки человека с помощью YOLOv8-pose.
        Возвращает структурированный словарь координат и уверенности для анализа.
        """
        res = self.model(frame, conf=0.4, imgsz=self.imgsz,
                         verbose=False, device=self.device)
        if not res or len(res[0].keypoints.data) == 0:
            self.smoother.reset()
            return None
        try:
            kp = res[0].keypoints.data[0].cpu().numpy()
            if kp.shape[0] < 17:
                return None

            self.orientation = detect_orientation(kp)
            side = get_best_side(kp)
            si, hi, ki, ai = get_side_indices(side)

            # Проверка базовой видимости ключевых точек для доминирующей стороны
            if any(kp[i][2] < 0.5 for i in [si, hi, ki, ai]):
                self.smoother.reset()
                return None

            raw = {
                "shoulder": [int(kp[si][0]), int(kp[si][1])],
                "hip": [int(kp[hi][0]), int(kp[hi][1])],
                "knee": [int(kp[ki][0]), int(kp[ki][1])],
                "ankle": [int(kp[ai][0]), int(kp[ai][1])],

                "knee_l": [int(kp[13][0]), int(kp[13][1])],
                "knee_l_conf": float(kp[13][2]),
                "knee_r": [int(kp[14][0]), int(kp[14][1])],
                "knee_r_conf": float(kp[14][2]),

                "ankle_l": [int(kp[15][0]), int(kp[15][1])],
                "ankle_l_conf": float(kp[15][2]),
                "ankle_r": [int(kp[16][0]), int(kp[16][1])],
                "ankle_r_conf": float(kp[16][2]),

                "hip_l": [int(kp[11][0]), int(kp[11][1])],
                "hip_l_conf": float(kp[11][2]),
                "hip_r": [int(kp[12][0]), int(kp[12][1])],
                "hip_r_conf": float(kp[12][2]),

                "shoulder_l": [int(kp[5][0]), int(kp[5][1])],
                "shoulder_l_conf": float(kp[5][2]),
                "shoulder_r": [int(kp[6][0]), int(kp[6][1])],
                "shoulder_r_conf": float(kp[6][2]),

                "side": side,
            }
            return self.smoother.smooth(raw)
        except Exception as e:
            logger.debug(f"Pose skip: {e}")
            self.smoother.reset()
            return None
