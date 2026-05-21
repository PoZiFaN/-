# filename: trainer/state_machine.py
"""UP/DOWN автомат с защитой от дребезга и двойной валидацией."""
import config
import logging
import math

logger = logging.getLogger("AITrainer.FSM")


class SquatStateMachine:
    def __init__(self):
        self.state = "UP"
        self._buf = 0

    def reset(self):
        self.state = "UP"
        self._buf = 0

    def update(self, knee_angle: int, squat_depth: int, reset_angle: int, points: dict, camera_orientation: str = "lateral") -> str:
        """
        Возвращает событие: 'REP_DONE', 'WENT_DOWN', '' (ничего).
        В зависимости от ракурса использует оптимальный биомеханический триггер глубины.
        """
        hip = points['hip']
        knee = points['knee']
        ankle = points['ankle']

        if camera_orientation == config.ORIENTATION_FRONTAL:
            # Во фронтальном ракурсе 2D-угол колена остается развернутым (около 180°).
            # Считаем отношение вертикального профиля бедра (knee Y - hip Y) к вертикальному профилю голени.
            shin_length = math.hypot(knee[0] - ankle[0], knee[1] - ankle[1])
            shin_length = max(shin_length, 10.0)

            vertical_dist = knee[1] - hip[1]
            ratio = vertical_dist / shin_length

            # Двойной замок для фронтального режима
            is_physically_up = (ratio > 0.65)
            is_physically_down = (ratio < 0.35)  # Таз опустился к уровню коленей
        else:
            # Классический режим сбоку (90 градусов): колено в 2D точно отражает биомеханический угол
            thigh_length = math.hypot(knee[0] - hip[0], knee[1] - hip[1])
            thigh_length = max(thigh_length, 10.0)

            vertical_dist = knee[1] - hip[1]
            ratio = vertical_dist / thigh_length

            is_physically_up = (knee_angle > reset_angle) and (ratio > 0.6)
            is_physically_down = (knee_angle < squat_depth) and (ratio < 0.5)

        if is_physically_up:
            if self.state == "DOWN":
                self._buf += 1
                if self._buf >= config.DEBOUNCE_FRAMES:
                    self.state = "UP"
                    self._buf = 0
                    logger.debug("FSM: DOWN → UP")
                    return "REP_DONE"
            else:
                self._buf = 0

        elif is_physically_down:
            if self.state == "UP":
                self._buf += 1
                if self._buf >= config.DEBOUNCE_FRAMES:
                    self.state = "DOWN"
                    self._buf = 0
                    logger.debug("FSM: UP → DOWN")
                    return "WENT_DOWN"
            else:
                self._buf = 0
        else:
            self._buf = 0

        return ""
