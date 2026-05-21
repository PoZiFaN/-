# filename: gui/sidebar.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QSpinBox, QGroupBox,
                              QProgressBar, QFormLayout, QComboBox)
from PyQt6.QtCore import Qt
import config


class Sidebar(QWidget):
    def __init__(self, on_start, on_stop, on_instruction):
        super().__init__()
        self.setFixedWidth(310)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.addWidget(self._build_session(on_start, on_stop))
        layout.addWidget(self._build_thresholds())
        layout.addWidget(self._build_live())

        btn_instr = QPushButton("📋  КАК ПРАВИЛЬНО СТОЯТЬ")
        btn_instr.clicked.connect(on_instruction)
        layout.addWidget(btn_instr)
        layout.addStretch()

    def _build_session(self, on_start, on_stop) -> QGroupBox:
        g = QGroupBox("Настройки сессии")
        l = QVBoxLayout(g)
        
        self.combo_orient = QComboBox()
        self.combo_orient.addItems(["Сбоку (90°)", "Спереди (0°)"])
        
        self.spin_target = QSpinBox()
        self.spin_target.setRange(1, 200)
        self.spin_target.setValue(10)
        
        self.btn_start = QPushButton("▶  СТАРТ")
        self.btn_stop  = QPushButton("■  СТОП")
        self.btn_stop.setObjectName("StopBtn")
        self.btn_stop.setEnabled(False)
        self.btn_start.clicked.connect(on_start)
        self.btn_stop.clicked.connect(on_stop)
        
        row = QHBoxLayout()
        row.addWidget(self.btn_start)
        row.addWidget(self.btn_stop)
        
        self.progress = QProgressBar()
        self.progress.setFormat("%v / %m повторов")
        
        l.addWidget(QLabel("Ракурс съемки:"))
        l.addWidget(self.combo_orient)
        l.addWidget(QLabel("Целевых повторов:"))
        l.addWidget(self.spin_target)
        l.addLayout(row)
        l.addWidget(self.progress)
        return g

    def _build_thresholds(self) -> QGroupBox:
        g = QGroupBox("Углы (настройка)")
        f = QFormLayout(g)
        self.spin_depth = self._spin(
            config.SQUAT_DEPTH_MIN, config.SQUAT_DEPTH_MAX, config.SQUAT_DEPTH)
        self.spin_reset = self._spin(
            config.RESET_ANGLE_MIN, config.RESET_ANGLE_MAX, config.RESET_ANGLE)
        self.spin_warn  = self._spin(
            config.WARN_OFFSET_MIN, config.WARN_OFFSET_MAX, config.WARN_OFFSET)
        self.spin_bad   = self._spin(
            config.BAD_OFFSET_MIN, config.BAD_OFFSET_MAX, config.BAD_OFFSET)
        f.addRow("Глубина приседа (°):", self.spin_depth)
        f.addRow("Угол выпрямления (°):", self.spin_reset)
        f.addRow("Наклон — предупреждение (°):", self.spin_warn)
        f.addRow("Наклон — ошибка (°):", self.spin_bad)
        return g

    def _build_live(self) -> QGroupBox:
        g = QGroupBox("Текущие показатели")
        l = QVBoxLayout(g)
        self.lbl_reps = QLabel("0")
        self.lbl_reps.setObjectName("StatsLabel")
        self.lbl_reps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_feedback = QLabel("ОЖИДАНИЕ")
        self.lbl_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(QLabel("Выполнено повторов:"))
        l.addWidget(self.lbl_reps)
        l.addWidget(QLabel("Подсказка:"))
        l.addWidget(self.lbl_feedback)
        return g

    @staticmethod
    def _spin(mn, mx, val) -> QSpinBox:
        s = QSpinBox()
        s.setRange(mn, mx)
        s.setValue(val)
        return s
