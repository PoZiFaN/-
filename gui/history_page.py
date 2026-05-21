# filename: gui/history_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                              QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui  import QColor


class HistoryPage(QWidget):
    def __init__(self, on_back):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("ИСТОРИЯ ТРЕНИРОВОК")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size:20px;font-weight:bold;color:#00adb5;")

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Дата и время", "Повторов", "Хороших", "% отлично"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)

        btn = QPushButton("← НАЗАД")
        btn.clicked.connect(on_back)

        layout.addWidget(title)
        layout.addWidget(self.table)
        layout.addWidget(btn)

    def populate(self, sessions):
        self.table.setRowCount(len(sessions))
        for row, s in enumerate(sessions):
            pct_color = (QColor("#00e676") if s["good_pct"] >= 80 else
                         QColor("#ffeb3b") if s["good_pct"] >= 50 else
                         QColor("#ff4444"))
            vals = [s["date"], str(s["total"]),
                    str(s["good"]), f"{s['good_pct']}%"]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                if col == 3:
                    item.setForeground(pct_color)
                self.table.setItem(row, col, item)