# filename: trainer/session.py
import logging
from trainer.session_state import SessionState
from trainer.engine import SquatEngine

logger = logging.getLogger("AITrainer.Session")


class Session:
    """
    Оркестратор (Директор).
    Связывает хранилище данных (State) и логику (Engine).
    """

    def __init__(self):
        self.state = SessionState()
        self._engine = SquatEngine()

    def start(self, target: int, **kwargs):
        """Запуск новой тренировки."""
        self.state.setup_new(target, **kwargs)
        self._engine.reset_all()
        logger.info(f"Сессия запущена через Engine. Цель: {target}")

    def stop(self):
        """Принудительная остановка."""
        self.state.active = False
        self.state.feedback = "ОСТАНОВЛЕНО"
        logger.info("Сессия остановлена.")

    def process(self, points: dict) -> bool:
        """Главный метод: обработка одного кадра."""
        if not self.state.active or points is None:
            return False

        # Делегируем всю работу двигателю
        return self._engine.drive(self.state, points)

    # --- Свойства для совместимости с UI (Отрисовка) ---
    @property
    def active(self): return self.state.active

    @property
    def mode(self): return self.state.mode

    @property
    def counter(self): return self.state.counter

    @property
    def target(self): return self.state.target

    @property
    def feedback(self): return self.state.feedback

    @property
    def color(self): return self.state.color

    @property
    def rep_history(self): return self.state.rep_history

    @property
    def current_knee_angle(self): return self.state.current_knee_angle

    @property
    def current_back_lean(self): return self.state.current_back_lean

    # ИСПРАВЛЕНО: Прокси-свойства для UI (ui/draw.py), чтобы он мог найти механизмы внутри Engine
    @property
    def _fsm(self):
        """Позволяет UI обращаться к session._fsm.state"""
        return self._engine._fsm

    @property
    def _calib(self):
        """Позволяет UI обращаться к session._calib.frames_collected"""
        return self._engine._calib