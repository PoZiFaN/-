# filename: trainer/engine.py
import logging
from trainer.session_state import SessionState
from trainer.frame_metrics import FrameMetrics
from trainer.state_machine import SquatStateMachine
from trainer.calibrator import Calibrator
from trainer.checker import FormChecker
from trainer.rep_tracker import RepTracker
from trainer.recorder import record_rep
from trainer.sound import SoundPlayer

logger = logging.getLogger("AITrainer.Engine")


class SquatEngine:
    """
    Двигатель логики (Мозг).
    Здесь принимаются решения, но сами данные хранятся в SessionState.
    """

    def __init__(self):
        self._fsm = SquatStateMachine()
        self._sound = SoundPlayer()
        self._calib = Calibrator()
        self._checker = FormChecker()
        self._tracker = RepTracker()

    def reset_all(self):
        """Полный сброс всех внутренних механизмов."""
        self._fsm.reset()
        self._calib.reset()
        self._checker.reset()
        self._tracker.reset()

    def drive(self, state: SessionState, points: dict) -> bool:
        """
        Главный цикл управления.
        Обновляет объект state и возвращает True, если тренировка окончена.
        """
        # 1. Обновляем показатели текущего кадра
        state.metrics = FrameMetrics.compute(points)

        # 2. Отрабатываем логику в зависимости от режима
        if state.mode == "CALIBRATION":
            return self._handle_calibration(state, points)

        return self._handle_training(state, points)

    def _handle_calibration(self, state: SessionState, points: dict) -> bool:
        if self._calib.update(points):
            state.mode = "TRAINING"
            state.feedback = "НАЧИНАЙ!"
            self._sound.play("GOOD")
        return False

    def _handle_training(self, state: SessionState, points: dict) -> bool:
        fsm_state = self._fsm.state

        # Журналируем экстремумы, если человек внизу
        if fsm_state == "DOWN":
            self._tracker.update_extremes(state.metrics, self._calib.baseline_lean)

        # Проверяем технику с учетом ракурса камеры
        state.feedback, state.color, checks = self._checker.check(
            points, fsm_state, self._calib.baseline_lean, state.camera_orientation
        )
        
        # Накапливаем ошибки в трекере за всё время текущего повторения
        self._tracker.accumulate(checks)

        # Проверяем фазу движения (Встал/Сел) с учетом ракурса камеры
        event = self._fsm.update(
            state.metrics.knee_angle,
            state.squat_depth,
            state.reset_angle,
            points,
            state.camera_orientation
        )

        if event == "WENT_DOWN":
            self._tracker.reset()

        if event == "REP_DONE":
            state.counter += 1

            # Записываем результат на основе накопленных за повторение ошибок
            rep = record_rep(
                state.counter,
                self._tracker.checks,
                self._tracker.max_lean,
                self._tracker.min_knee,
                self._tracker.min_ratio
            )
            state.rep_history.append(rep)
            self._sound.play("GOOD" if rep.quality == "GOOD" else "BAD")

            self._tracker.reset()

            if state.counter >= state.target:
                state.active = False
                self._sound.play("DONE")
                return True

        return False

    @property
    def fsm_state(self) -> str:
        return self._fsm.state

    @property
    def frames_collected(self) -> int:
        return self._calib.frames_collected
