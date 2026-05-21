# filename: trainer/checker.py
import config
import logging
from analysis.lateral_checks import check_back_lean, check_knee_over_toe
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

    def reset(self):
        self.speed.reset()
        self.stability.reset()
        self._error_counters.clear()

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

    def check(self, points: dict, state: str,
              baseline: int, camera_orientation: str = "lateral") -> tuple[str, tuple, RepChecks]:
        """
        Проверяет форму в реальном времени с защитой от мерцания.
        Активирует только валидные проверки для текущего ракурса камеры.
        """
        checks = RepChecks()
        feedbacks = []

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

        elif camera_orientation == config.ORIENTATION_FRONTAL:
            # РАКУРС СПЕРЕДИ (0°): Анализ завала коленей (вальгуса) и симметрии приседаний
            if state == "DOWN":
                raw_v_msg, raw_v_sev = check_valgus(points)
                v_msg, v_sev = self._debounce("valgus", raw_v_msg, raw_v_sev, custom_limit=5)
                if v_sev:
                    checks.knee_severities.append(v_sev)
                    checks.add_issue(v_msg, v_sev)
                    feedbacks.append((v_msg, v_sev))

                raw_s_msg, raw_s_sev = check_symmetry(points)
                s_msg, s_sev = self._debounce("symmetry", raw_s_msg, raw_s_sev, custom_limit=5)
                if s_sev:
                    checks.other_severities.append(s_sev)
                    checks.add_issue(s_msg, s_sev)
                    feedbacks.append((s_msg, s_sev))
            else:
                self._error_counters["valgus"] = 0
                self._error_counters["symmetry"] = 0

        # Общесистемные проверки темпа и стабильности (выполняются всегда)
        self.speed.update(state)
        self.stability.update(points, state)

        # Скорость спуска (только в лог сессии, без засорения экрана)
        raw_spd_msg, raw_spd_sev = self.speed.check_descent()
        spd_msg, spd_sev = self._debounce("speed_descent", raw_spd_msg, raw_spd_sev)
        if spd_sev:
            checks.speed_severities.append(spd_sev)
            checks.add_issue(raw_spd_msg, spd_sev)

        # Скорость подъема
        raw_asc_msg, raw_asc_sev = self.speed.check_ascent()
        asc_msg, asc_sev = self._debounce("speed_ascent", raw_asc_msg, raw_asc_sev)
        if asc_sev:
            checks.speed_severities.append(asc_sev)
            checks.add_issue(raw_asc_msg, asc_sev)

        # Дрожание (нестабильность) коленей
        raw_stb_msg, raw_stb_sev = self.stability.check()
        stb_msg, stb_sev = self._debounce("stability", raw_stb_msg, raw_stb_sev)
        if stb_sev:
            checks.other_severities.append(stb_sev)
            checks.add_issue(stb_msg, stb_sev)
            feedbacks.append((stb_msg, stb_sev))

        # Выбираем приоритетное текстовое замечание для UI
        feedback, color = self._pick_worst(feedbacks)
        return feedback, color, checks

    @staticmethod
    def _pick_worst(feedbacks: list) -> tuple[str, tuple]:
        if not feedbacks:
            return "ХОРОШАЯ ФОРМА", config.GREEN

        priority = {"BAD": 2, "WARNING": 1, "": 0}
        msg, sev = max(feedbacks, key=lambda x: priority.get(x[1], 0))

        color = (config.RED if sev == "BAD" else
                 config.YELLOW if sev == "WARNING" else
                 config.GREEN)
        return msg, color
