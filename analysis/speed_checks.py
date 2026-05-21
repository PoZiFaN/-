# filename: analysis/speed_checks.py
"""Проверка скорости фаз спуска и подъёма в реальном времени."""
import time
import config


class SpeedTracker:
    def __init__(self):
        self.descent_start_time = 0.0
        self.ascent_start_time = 0.0
        self.descent_duration = 0.0
        self.ascent_duration = 0.0
        self._phase = "idle"   # idle / descending / ascending

    def reset(self):
        self.descent_start_time = 0.0
        self.ascent_start_time = 0.0
        self.descent_duration = 0.0
        self.ascent_duration = 0.0
        self._phase = "idle"

    def update(self, state: str):
        """state: 'UP' или 'DOWN' из state_machine."""
        now = time.perf_counter()
        
        if state == "DOWN" and self._phase != "descending":
            self._phase = "descending"
            self.descent_start_time = now
            self.descent_duration = 0.0
        elif state == "UP" and self._phase == "descending":
            self._phase = "ascending"
            self.ascent_start_time = now
            self.descent_duration = now - self.descent_start_time
            self.ascent_duration = 0.0

        if self._phase == "descending":
            self.descent_duration = now - self.descent_start_time
        elif self._phase == "ascending":
            self.ascent_duration = now - self.ascent_start_time

    def check_descent(self) -> tuple[str, str]:
        """
        Проверяет скорость спуска на основе реального времени (time.perf_counter()).
        Возвращает текстовое имя нарушения и его критичность для RepChecks.
        """
        min_time = getattr(config, "MIN_DESCENT_TIME", 0.5)
        if 0 < self.descent_duration < min_time:
            return "СЛИШКОМ БЫСТРЫЙ СПУСК", "WARNING"
        return "", ""

    def check_ascent(self) -> tuple[str, str]:
        """
        Проверяет скорость подъема на основе реального времени.
        Возвращает текстовое имя нарушения и его критичность для RepChecks.
        """
        min_time = config.MIN_ASCENT_FRAMES / config.TARGET_FPS
        if 0 < self.ascent_duration < min_time:
            return "БЫСТРЫЙ ПОДЪЕМ", "WARNING"
        return "", ""
