# filename: gui/worker.py
import cv2
import logging
import time
import platform
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui  import QImage
import config
from core.pose_detector import PoseDetector
from trainer            import Session
from ui.draw            import draw

logger = logging.getLogger("AITrainer.Worker")


class VisionWorker(QThread):
    frame_signal    = pyqtSignal(QImage)
    stats_signal    = pyqtSignal(int, str, str)
    finished_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._run    = True
        self.session = Session()
        self.pose    = PoseDetector()

    def run(self):
        camera_id = config.get_camera_id()
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            logger.error("Камера не найдена. Остановка потока.")
            return

        # Принудительно снижаем разрешение камеры, чтобы не грузить процессор
        # декодированием лишних пикселей (экономия ОЗУ и ЦП)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

        target_frame_time = 1.0 / config.TARGET_FPS

        while self._run:
            start_time = time.perf_counter()

            ret, frame = cap.read()
            if not ret:
                logger.warning("Потерян кадр с камеры. Ожидание восстановления...")
                self.msleep(100)
                continue

            points    = self.pose.find_pose(frame)
            done      = self.session.process(points)
            annotated = draw(frame, self.session, points)

            self.frame_signal.emit(self._to_qt(annotated))
            self.stats_signal.emit(
                self.session.counter,
                self.session.feedback,
                self.session.mode)

            if done:
                self.finished_signal.emit(self.session)

            # Точный лимитер FPS (удерживает ровно 15 кадров в секунду)
            # Защищает ноутбук от перегрева и 100% загрузки процессора
            elapsed = time.perf_counter() - start_time
            sleep_time = target_frame_time - elapsed
            if sleep_time > 0:
                self.msleep(int(sleep_time * 1000))

        cap.release()

    def stop(self):
        self._run = False
        self.wait()

    def start_session(self, target, **kw):
        self.session.start(target, **kw)

    def _to_qt(self, img) -> QImage:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        return QImage(rgb.data, w, h, ch * w,
                      QImage.Format.Format_RGB888).copy()
