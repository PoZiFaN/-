# filename: gui/main_window.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage
import logging
import config
from gui.worker import VisionWorker
from gui.sidebar import Sidebar
from gui.results_page import ResultsPage
from gui.history_page import HistoryPage
from gui.instruction_page import InstructionPage
from gui.navigation_controller import NavigationController

logger = logging.getLogger("AITrainer.Window")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Тренер Приседаний")
        self.resize(1280, 820)

        # Выделение управления переходами в независимый контроллер
        self.nav_controller = NavigationController(self)

        self.sidebar = Sidebar(
            on_start=self.start_session,
            on_stop=self.stop_session,
            on_instruction=self.nav_controller.go_to_instruction
        )

        self.stack = QStackedWidget()

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet(
            "background:#000;border-radius:8px;")

        self.results_page = ResultsPage(
            on_new=self.nav_controller.go_to_video,
            on_history=self.nav_controller.go_to_history
        )

        self.history_page = HistoryPage(
            on_back=self.nav_controller.go_to_video
        )

        self.instruction_page = InstructionPage(
            on_back=self.nav_controller.go_to_video
        )

        # Регистрация страниц в менеджере компоновки (стеке)
        self.stack.addWidget(self.video_label)       # Индекс 0 (PAGE_VIDEO)
        self.stack.addWidget(self.results_page)      # Индекс 1 (PAGE_RESULTS)
        self.stack.addWidget(self.history_page)      # Индекс 2 (PAGE_HISTORY)
        self.stack.addWidget(self.instruction_page)  # Индекс 3 (PAGE_INSTRUCTION)

        root = QHBoxLayout(self)
        root.addWidget(self.sidebar)
        root.addWidget(self.stack, stretch=1)

        self.worker = VisionWorker()
        self.worker.frame_signal.connect(self.update_frame)
        self.worker.stats_signal.connect(self.update_stats)
        self.worker.finished_signal.connect(self.nav_controller.go_to_results)
        self.worker.start()
        logger.info("Окно готово.")

    def start_session(self):
        sb = self.sidebar
        target = sb.spin_target.value()
        sb.progress.setRange(0, target)
        sb.progress.setValue(0)
        
        # Получаем ракурс камеры из интерфейса
        orient_text = sb.combo_orient.currentText()
        camera_orientation = config.ORIENTATION_LATERAL if "Сбоку" in orient_text else config.ORIENTATION_FRONTAL

        self.worker.start_session(
            target,
            squat_depth=sb.spin_depth.value(),
            reset_angle=sb.spin_reset.value(),
            warn_offset=sb.spin_warn.value(),
            bad_offset=sb.spin_bad.value(),
            camera_orientation=camera_orientation
        )
        self.nav_controller.go_to_video()
        sb.btn_start.setEnabled(False)
        sb.btn_start.setText("ИДЁТ ТРЕНИРОВКА...")
        sb.btn_stop.setEnabled(True)

    def stop_session(self):
        self.worker.session.stop()
        self.nav_controller.go_to_results(self.worker.session)

    def _reset_buttons(self):
        self.sidebar.btn_start.setEnabled(True)
        self.sidebar.btn_start.setText("▶  СТАРТ")
        self.sidebar.btn_stop.setEnabled(False)

    @pyqtSlot(QImage)
    def update_frame(self, img):
        if self.stack.currentIndex() == 0:  # PAGE_VIDEO
            self.video_label.setPixmap(QPixmap.fromImage(img))

    @pyqtSlot(int, str, str)
    def update_stats(self, reps, feedback, mode):
        self.sidebar.lbl_reps.setText(str(reps))
        self.sidebar.lbl_feedback.setText(feedback)
        self.sidebar.progress.setValue(reps)
        color = ("#00e676" if "ХОРОШАЯ" in feedback else
                 "#ff4444" if any(w in feedback for w in
                                  ["ОПАСНО", "ВПЕРЁД", "ОШИБКА"]) else
                 "#888"    if "СТОП"    in feedback else
                 "#ffeb3b")
        self.sidebar.lbl_feedback.setStyleSheet(
            f"color:{color};font-size:14px;font-weight:bold;")

    def closeEvent(self, event):
        self.worker.stop()
        super().closeEvent(event)
