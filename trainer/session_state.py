# filename: trainer/session_state.py
import config
from dataclasses import dataclass, field
from trainer.frame_metrics import FrameMetrics


@dataclass
class SessionState:
    """
    Чистое хранилище данных (Секретарь).
    Содержит только переменные, которые нужны интерфейсу для отрисовки.
    """
    active: bool = False
    mode: str = "IDLE"
    counter: int = 0
    target: int = 0
    rep_history: list = field(default_factory=list)
    feedback: str = "ОЖИДАНИЕ"
    color: tuple = config.WHITE
    metrics: FrameMetrics | None = None

    squat_depth: int = config.SQUAT_DEPTH
    reset_angle: int = config.RESET_ANGLE
    warn_offset: int = config.WARN_OFFSET
    bad_offset: int = config.BAD_OFFSET
    camera_orientation: str = config.ORIENTATION_LATERAL

    def setup_new(self, target: int, **kwargs):
        """Сбрасывает переменные для новой тренировки."""
        self.active = True
        self.mode = "CALIBRATION"
        self.counter = 0
        self.target = target
        self.rep_history = []
        self.feedback = "КАЛИБРОВКА..."
        self.color = config.WHITE

        self.squat_depth = kwargs.get('squat_depth') or config.SQUAT_DEPTH
        self.reset_angle = kwargs.get('reset_angle') or config.RESET_ANGLE
        self.warn_offset = kwargs.get('warn_offset') or config.WARN_OFFSET
        self.bad_offset = kwargs.get('bad_offset') or config.BAD_OFFSET
        self.camera_orientation = kwargs.get('camera_orientation') or config.ORIENTATION_LATERAL

    # Свойства-переходники для графического интерфейса
    @property
    def current_knee_angle(self) -> int:
        return self.metrics.knee_angle if self.metrics else 180

    @property
    def current_back_lean(self) -> int:
        return self.metrics.back_lean if self.metrics else 0
