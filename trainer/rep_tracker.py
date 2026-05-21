# filename: trainer/rep_tracker.py
from trainer.frame_metrics import FrameMetrics
from analysis.rep_scorer import RepChecks


class RepTracker:
    """
    Отслеживает экстремумы (максимумы и минимумы) во время одного приседания.
    Сбрасывается при начале каждого нового повторения.
    """
    def __init__(self):
        self.max_lean: float = 0.0
        self.min_knee: float = 180.0
        self.min_ratio: float = 1.0
        self.checks: RepChecks = RepChecks()

    def reset(self):
        """Очищает память перед новым повторением."""
        self.max_lean = 0.0
        self.min_knee = 180.0
        self.min_ratio = 1.0
        self.checks = RepChecks()

    def update_extremes(self, metrics: FrameMetrics, baseline_lean: int):
        """
        Обновляет рекорды за повторение.
        Нам важно поймать момент самого сильного наклона и самого глубокого приседа.
        """
        # 1. Максимальный наклон спины (считаем абсолютное значение угла наклона спины в градусах)
        # Это полностью исключает появление значений 0° на итоговом экране результатов.
        if metrics.back_lean > self.max_lean:
            self.max_lean = metrics.back_lean

        # 2. Минимальный угол колена (самая глубокая точка по углам)
        if metrics.knee_angle < self.min_knee:
            self.min_knee = metrics.knee_angle

        # 3. Минимальная высота таза (самая глубокая точка по координатам)
        if metrics.hip_ratio < self.min_ratio:
            self.min_ratio = metrics.hip_ratio

    def accumulate(self, checks: RepChecks):
        """
        Накапливает все обнаруженные ошибки за время повторения.
        Решает критический баг затирания ошибок последующими чистыми кадрами.
        """
        for sev in checks.back_severities:
            if sev not in self.checks.back_severities:
                self.checks.back_severities.append(sev)
        for sev in checks.knee_severities:
            if sev not in self.checks.knee_severities:
                self.checks.knee_severities.append(sev)
        for sev in checks.speed_severities:
            if sev not in self.checks.speed_severities:
                self.checks.speed_severities.append(sev)
        for sev in checks.other_severities:
            if sev not in self.checks.other_severities:
                self.checks.other_severities.append(sev)
        for msg in checks.messages:
            if msg and msg not in self.checks.messages:
                self.checks.messages.append(msg)
