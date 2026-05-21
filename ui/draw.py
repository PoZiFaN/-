# filename: ui/draw.py
import cv2
import config
from ui.text_renderer import put_text
from ui.overlay import draw_skeleton, draw_metrics
from ui.hud import draw_training_hud, draw_calibration_bar
from ui.orientation_prompt import draw_position_hint


def draw(frame, session, points):
    h, w = frame.shape[:2]

    camera_orientation = getattr(session.state, "camera_orientation", config.ORIENTATION_LATERAL)

    if points is None:
        frame = put_text(frame, "ЧЕЛОВЕК НЕ ОБНАРУЖЕН",
                         (w//2 - 200, h//2),
                         size=30, color=config.RED)
        frame = draw_position_hint(frame, camera_orientation)
        return frame

    back_color = session.color if session.mode == "TRAINING" else config.WHITE
    draw_skeleton(frame, points, back_color, camera_orientation)

    if session.mode == "TRAINING":
        frame = draw_metrics(frame, points,
                             session.current_knee_angle,
                             session.current_back_lean,
                             back_color,
                             camera_orientation)
        frame = draw_training_hud(frame, session.counter, session.target,
                                  session.feedback, session.color,
                                  session._fsm.state)

    elif session.mode == "CALIBRATION":
        frame = draw_calibration_bar(frame, session._calib.frames_collected)

    frame = draw_position_hint(frame, camera_orientation)
    return frame
