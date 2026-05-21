# filename: storage/csv_reader.py
import os, csv, logging
from typing import List

logger = logging.getLogger("AITrainer.CSV")


def load_all(folder: str = "sessions_history") -> List[dict]:
    if not os.path.isdir(folder):
        return []
    sessions = []
    for fname in sorted(os.listdir(folder), reverse=True):
        if not fname.endswith(".csv"):
            continue
        try:
            with open(f"{folder}/{fname}", newline="", encoding="utf-8") as f:
                rows = [r for r in csv.reader(f)
                        if len(r) >= 2 and r[0].isdigit()]
            total    = len(rows)
            good     = sum(1 for r in rows if r[1] == "GOOD")
            good_pct = round(good / total * 100) if total else 0
            date_str = fname.replace("session_","").replace(".csv","").replace("_"," ")
            sessions.append({"date": date_str, "total": total,
                             "good": good, "good_pct": good_pct})
        except Exception as e:
            logger.warning(f"Can't read {fname}: {e}")
    return sessions


def get_summary(rep_history: list) -> dict:
    if not rep_history:
        return {}
    import numpy as np
    total = len(rep_history)
    good  = sum(1 for r in rep_history if r.quality == "GOOD")
    warn  = sum(1 for r in rep_history if r.quality == "WARNING")
    bad   = sum(1 for r in rep_history if r.quality == "BAD")
    return {
        "total": total, "good": good, "warning": warn, "bad": bad,
        "good_pct":  round(good / total * 100),
        "avg_lean":  round(float(np.mean([r.max_back_lean  for r in rep_history])), 1),
        "avg_depth": round(float(np.mean([r.min_knee_angle for r in rep_history])), 1),
    }