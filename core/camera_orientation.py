# filename: core/camera_orientation.py

# При концепции 45° ориентация всегда одна
DIAGONAL = "diagonal"

def detect_orientation(keypoints) -> str:
    return DIAGONAL