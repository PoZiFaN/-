# filename: trainer/recorder.py
import logging
from analysis.rep_scorer import RepChecks, score_rep
from trainer.rep_result import RepResult

logger = logging.getLogger("AITrainer.Recorder")


def record_rep(counter: int,
               checks: RepChecks,
               max_lean: float,
               min_knee: float,
               min_ratio: float) -> RepResult:
    """
    Формирует итоговый объект результата для одного приседания.
    """
    # 1. Получаем финальную оценку качества (GOOD/WARNING/BAD)
    quality = score_rep(checks, min_ratio)

    # 2. Собираем уникальные сообщения об ошибках
    issues = list(dict.fromkeys(checks.messages))

    # 3. Создаем объект результата
    result = RepResult(
        rep_number=counter,
        quality=quality,
        max_back_lean=int(max_lean),
        min_knee_angle=int(min_knee),
        issues=issues
    )

    logger.info(f"REP {counter} SAVED: Quality={quality}, MaxLean={max_lean}")
    return result