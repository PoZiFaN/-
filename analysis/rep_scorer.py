# filename: analysis/rep_scorer.py
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class RepChecks:
    """Хранилище всех нарушений за одно повторение."""
    back_severities: list = field(default_factory=list)
    knee_severities: list = field(default_factory=list)
    speed_severities: list = field(default_factory=list)
    other_severities: list = field(default_factory=list)

    # Текстовые описания для итоговой таблицы
    messages: list = field(default_factory=list)

    def add_issue(self, msg: str, severity: str):
        """Добавляет текст ошибки, если его еще нет в списке."""
        if msg and msg not in self.messages:
            self.messages.append(msg)

    def worst(self) -> Literal["GOOD", "WARNING", "BAD"]:
        """Определяет общую оценку на основе всех корзин тяжести."""
        all_s = (self.back_severities + self.knee_severities +
                 self.speed_severities + self.other_severities)
        if "BAD" in all_s:
            return "BAD"
        if "WARNING" in all_s:
            return "WARNING"
        return "GOOD"


def score_rep(checks: RepChecks, min_ratio: float) -> Literal["GOOD", "WARNING", "BAD"]:
    """
    Финальная оценка качества повторения.
    """
    # Проверка глубины по соотношению координат таза/колена
    if min_ratio > 0.25:
        checks.add_issue("НЕДОСЕД (ПОЛУПРИСЕД)", "WARNING")
        checks.other_severities.append("WARNING")
    elif min_ratio > 0.10:
        checks.add_issue("ПРИСЕДАЙ ЧУТЬ ГЛУБЖЕ", "WARNING")
        checks.other_severities.append("WARNING")

    return checks.worst()