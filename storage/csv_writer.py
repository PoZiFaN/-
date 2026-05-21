# filename: storage/csv_writer.py
import os, csv, logging
from datetime import datetime

logger = logging.getLogger("AITrainer.CSV")


def save_session(rep_history: list, folder: str = "sessions_history") -> str:
    if not rep_history:
        return ""
    os.makedirs(folder, exist_ok=True)
    ts       = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{folder}/session_{ts}.csv"
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Rep", "Quality", "Max Lean", "Min Knee", "Issues"])
            for r in rep_history:
                w.writerow([r.rep_number, r.quality,
                             r.max_back_lean, r.min_knee_angle,
                             "|".join(r.issues)])
            # итог
            good = sum(1 for r in rep_history if r.quality == "GOOD")
            w.writerow([])
            w.writerow(["TOTAL", len(rep_history), "GOOD", good])
        logger.info(f"Saved: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Save failed: {e}")
        return ""