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
        # Отключено по требованию пользователя во избежание ложных подсказок скорости
        return "", ""

    def check_ascent(self) -> tuple[str, str]:
        # Отключено по требованию пользователя во избежание ложных подсказок скорости
        return "", ""
