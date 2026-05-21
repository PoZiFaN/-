# filename: trainer/calibrator.py
import numpy as np
import config
import logging
from analysis.angles import calculate_inclination

logger = logging.getLogger("AITrainer.Calibrator")


class Calibrator:
    def __init__(self):
        self.baseline_lean = 0
        self._frames: list = []
        self._done = False

    def reset(self):
        self.baseline_lean = 0
        self._frames       = []
        self._done         = False

    @property
    def is_done(self) -> bool:
        return self._done

    @property
    def frames_collected(self) -> int:
        return len(self._frames)

    def update(self, points: dict) -> bool:
        """
        Добавляет кадр. Возвращает True когда калибровка завершена.
        """
        if self._done:
            return True

        # Вычисляем наклон спины по инвариантной формуле
        lean = calculate_inclination(points['shoulder'], points['hip'])
        self._frames.append(lean)

        if len(self._frames) >= config.CALIBRATION_FRAMES:
            self.baseline_lean = int(np.mean(self._frames))
            self._done = True
            logger.info(f"Калибровка завершена. Базовый наклон={self.baseline_lean}°")
            return True

        return False
