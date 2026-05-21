# filename: core/side_detector.py

def get_best_side(keypoints) -> str:
    """
    Выбирает сторону тела с лучшим суммарным confidence.
    COCO: left=5,11,13,15 / right=6,12,14,16
    """
    left_conf  = sum(keypoints[i][2] for i in [5, 11, 13, 15])
    right_conf = sum(keypoints[i][2] for i in [6, 12, 14, 16])
    return "left" if left_conf >= right_conf else "right"


def get_side_indices(side: str) -> tuple:
    """Возвращает индексы (shoulder, hip, knee, ankle) для выбранной стороны."""
    if side == "left":
        return 5, 11, 13, 15
    return 6, 12, 14, 16