# filename: trainer/checker.py
import config
import logging
from analysis.angles import calculate_inclination, calculate_angle
from analysis.lateral_checks import (
    check_back_lean, 
    check_knee_over_toe, 
    check_lumbar_bounce, 
    check_hip_drive_error
)
from analysis.frontal_checks import check_valgus, check_symmetry
from analysis.speed_checks import SpeedTracker
from analysis.stability_checks import StabilityTracker
from analysis.rep_scorer import RepChecks

logger = logging.getLogger("AITrainer.Checker")


class FormChecker:
    def __init__(self):
        self.speed = SpeedTracker()
        self.stability = StabilityTracker()
        # Хранилище счетчиков кадров для каждой проверки (Debounce)
        self._error_counters: dict[str, int] = {}
        # Буферы истории для динамических биомеханических расчетов
        self.back_lean_history = []
        self.knee_angle_history = []

    def reset(self):
        self.speed.reset()
        self.stability.reset()
        self._error_counters.clear()
        self.back_lean_history.clear()
        self.knee_angle_history.clear()

    def _debounce(self, key: str, msg: str, sev: str, custom_limit: int = None) -> tuple[str, str]:
        """
        Механизм антидребезга. Ошибка регистрируется только если она 
        присутствует ERROR_DEBOUNCE_FRAMES (или custom_limit) кадров подряд.
        """
        if not msg:
            self._error_counters[key] = 0
            return "", ""
        
        self._error_counters[key] = self._error_counters.get(key, 0) + 1
        
        limit = custom_limit if custom_limit is not None else config.ERROR_DEBOUNCE_FRAMES
        if self._error_counters[key] >= limit:
            return msg, sev
            
        return "", ""

    def _get_phase_instruction(self, state: str) -> str:
        """
        Генерирует динамическое, поддерживающее сообщение в зависимости от фазы выполнения приседа.
        """
        phase = self.speed._phase
        if state == "DOWN":
            return "ОТЛИЧНО, ДЕРЖИ ГЛУБИНУ!"
        if phase == "descending":
            return "ОПУСКАЙСЯ ПЛАВНО..."
        if phase == "ascending":
            return "ПОДЪЁМ"
        return "НАЧИНАЙ ПРИСЕДАНИЕ"

    def check(self, points: dict, state: str,
              baseline: int, camera_orientation: str = "lateral") -> tuple[str, tuple, RepChecks]:
        """
        Проверяет форму в реальном времени с защитой от мерцания.
        Активирует только валидные проверки для текущего ракурса камеры.
        """
        checks = RepChecks()
        feedbacks = []

        # Сбор и наполнение скользящих буферов истории углов
        current_lean = calculate_inclination(points['shoulder'], points['hip'])
        knee_angle = calculate_angle(points['hip'], points['knee'], points['ankle'])

        self.back_lean_history.append(current_lean)
        self.knee_angle_history.append(knee_angle)

        if len(self.back_lean_history) > 30:
            self.back_lean_history.pop(0)
        if len(self.knee_angle_history) > 30:
                self.knee_angle_history.pop(0)

        # Общесистемные обновления фазы и стабильности
        self.speed.update(state)
        self.stability.update(points, state)
        phase = self.speed._phase

        if camera_orientation == config.ORIENTATION_LATERAL:
            # РАКУРС СБОКУ (90°): Анализ наклона корпуса и положения колена относительно стопы
            raw_back_msg, raw_back_sev = check_back_lean(points, baseline)
            back_msg, back_sev = self._debounce("back_lean", raw_back_msg, raw_back_sev)
            if back_sev:
                checks.back_severities.append(back_sev)
                checks.add_issue(back_msg, back_sev)
                feedbacks.append((back_msg, back_sev))

            if state == "DOWN":
                raw_k_msg, raw_k_sev = check_knee_over_toe(points)
                k_msg, k_sev = self._debounce("knee_toe", raw_k_msg, raw_k_sev)
                if k_sev:
                    checks.knee_severities.append(k_sev)
                    checks.add_issue(k_msg, k_sev)
                    feedbacks.append((k_msg, k_sev))
            else:
                self._error_counters["knee_toe"] = 0

            # 1. Проверка двойного движения поясницей во время спуска
            raw_l_msg, raw_l_sev = check_lumbar_bounce(self.back_lean_history, phase)
            l_msg, l_sev = self._debounce("lumbar_bounce", raw_l_msg, raw_l_sev, custom_limit=3)
            if l_sev:
                checks.other_severities.append(l_sev)
                checks.add_issue(l_msg, l_sev)
                feedbacks.append((l_msg, l_sev))

            # 2. Проверка завала спины / резкого подъема с задом во время подъема (Good Morning Squat)
            raw_h_msg, raw_h_sev = check_hip_drive_error(
                self.back_lean_history, 
                self.knee_angle_history, 
                phase, 
                baseline
            )
            h_msg, h_sev = self._debounce("hip_drive", raw_h_msg, raw_h_sev, custom_limit=2)
            if h_sev:
                # Если критическая ошибка резкого подъема с тазом
                if h_sev == "BAD":
                    checks.back_severities.append(h_sev)
                else:
                    checks.other_severities.append(h_sev)
                checks.add_issue(h_msg, h_sev)
                feedbacks.append((h_msg, h_sev))

        elif camera_orientation == config.ORIENTATION_FRONTAL:
            # РАКУРС СПЕРЕДИ (0°): Анализ завала коленей (вальгуса) и симметрии приседаний
            if state == "DOWN":
                raw_v_msg, raw_v_sev = check_valgus(points)
                v_msg, v_sev = self._debounce("valgus", raw_v_msg, raw_v_sev, custom_limit=3)
                if v_sev:
                    checks.knee_severities.append(v_sev)
                    checks.add_issue(v_msg, v_sev)
                    feedbacks.append((v_msg, v_sev))

                raw_s_msg, raw_s_sev = check_symmetry(points)
                s_msg, s_sev = self._debounce("symmetry", raw_s_msg, raw_s_sev, custom_limit=3)
                if s_sev:
                    checks.other_severities.append(s_sev)
                    checks.add_issue(s_msg, s_sev)
                    feedbacks.append((s_msg, s_sev))
            else:
                self._error_counters["valgus"] = 0
                self._error_counters["symmetry"] = 0

        # Выбираем приоритетное текстовое замечание для UI
        feedback, color = self._pick_worst(feedbacks, state)
        return feedback, color, checks

    def _pick_worst(self, feedbacks: list, state: str) -> tuple[str, tuple]:
        """
        Приоритезация замечаний. Если ошибок нет, возвращает поддерживающую
        инструкцию в зависимости от текущей фазы движения.
        """
        if not feedbacks:
            msg = self._get_phase_instruction(state)
            return msg, config.GREEN

        priority = {"BAD": 2, "WARNING": 1, "": 0}
        msg, sev = max(feedbacks, key=lambda x: priority.get(x[1], 0))

        color = (config.RED if sev == "BAD" else
                 config.YELLOW if sev == "WARNING" else
                 config.GREEN)
        return msg, color
