# filename: gui/results_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                              QTableWidget, QTableWidgetItem,
                              QHeaderView, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor

QUALITY_COLORS = {
    "GOOD":    QColor("#00e676"),
    "WARNING": QColor("#ffeb3b"),
    "BAD":     QColor("#ff4444"),
}
QUALITY_RU = {
    "GOOD":    "ХОРОШО",
    "WARNING": "ПРЕДУПРЕЖДЕНИЕ",
    "BAD":     "ОШИБКА",
}


class ResultsPage(QWidget):
    def __init__(self, on_new, on_history):
        super().__init__()
        layout = QVBoxLayout(self)

        self.lbl_title = QLabel("ТРЕНИРОВКА ЗАВЕРШЕНА")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setStyleSheet(
            "font-size:22px;font-weight:bold;color:#00adb5;")

        self.lbl_summary = QLabel("")
        self.lbl_summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_summary.setWordWrap(True)
        self.lbl_summary.setStyleSheet("color:#aaa;font-size:12px;")

        self.lbl_path = QLabel("")
        self.lbl_path.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_path.setStyleSheet("color:#666;font-size:11px;")

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["№", "Качество", "Макс. наклон", "Мин. угол колена", "Нарушения"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)

        row = QHBoxLayout()
        btn_new  = QPushButton("▶  НОВАЯ СЕССИЯ")
        btn_hist = QPushButton("📋  ИСТОРИЯ")
        btn_new.clicked.connect(on_new)
        btn_hist.clicked.connect(on_history)
        row.addWidget(btn_new)
        row.addWidget(btn_hist)

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_summary)
        layout.addWidget(self.lbl_path)
        layout.addWidget(self.table)
        layout.addLayout(row)

    def populate(self, rep_history, summary, saved_path):
        self.lbl_path.setText(
            f"Сохранено: {saved_path}" if saved_path
            else "Не удалось сохранить.")
        if summary:
            self.lbl_summary.setText(
                f"Всего: {summary['total']}  "
                f"✅ Хорошо: {summary['good']}  "
                f"⚠️ Предупреждений: {summary['warning']}  "
                f"❌ Ошибок: {summary['bad']}  "
                f"({summary['good_pct']}% отлично)  |  "
                f"Средний наклон: {summary['avg_lean']}°  "
                f"Средняя глубина: {summary['avg_depth']}°")

        self.table.setRowCount(len(rep_history))
        for row, r in enumerate(rep_history):
            color = QUALITY_COLORS.get(r.quality, QColor("#fff"))
            items = [
                str(r.rep_number),
                QUALITY_RU.get(r.quality, r.quality),
                f"{r.max_back_lean}°",
                f"{r.min_knee_angle}°",
                ", ".join(r.issues) if r.issues else "—",
            ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                if col == 1:
                    item.setForeground(color)
                self.table.setItem(row, col, item)