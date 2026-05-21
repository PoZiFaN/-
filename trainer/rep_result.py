# filename: trainer/rep_result.py
from dataclasses import dataclass
from typing import Literal


@dataclass
class RepResult:
    rep_number:     int
    quality:        Literal["GOOD", "WARNING", "BAD"]
    max_back_lean:  int
    min_knee_angle: int
    issues:         list   # список строк с нарушениями