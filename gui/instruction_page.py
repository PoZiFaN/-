# filename: gui/instruction_page.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                              QPushButton, QScrollArea, QFrame)
from PyQt6.QtCore import Qt


class InstructionPage(QWidget):
    def __init__(self, on_back):
        super().__init__()
        layout = QVBoxLayout(self)

        title = QLabel("КАК ПРАВИЛЬНО ВСТАТЬ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size:20px;font-weight:bold;color:#00adb5;padding:10px;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setSpacing(12)

        sections = [
            ("📱  ПОЛОЖЕНИЕ ТЕЛЕФОНА",
             "• Поставь телефон сбоку и немного спереди — угол примерно 45°\n"
             "• Высота камеры — уровень бедра или чуть ниже\n"
             "• Телефон должен видеть тебя полностью — от головы до пола\n"
             "• Расстояние: 2–3 метра от тебя"),

            ("🦶  ПОСТАНОВКА НОГ",
             "• Ноги на ширине плеч или чуть шире\n"
             "• Носки развёрнуты наружу на 15–30°\n"
             "• Стопы стоят полностью на полу — не отрывай пятки\n"
             "• Вес равномерно распределён по всей стопе"),

            ("🦵  ДВИЖЕНИЕ ВНИЗ",
             "• Начинай движение с отведения таза назад\n"
             "• Колени двигаются в сторону носков — не внутрь!\n"
             "• Опускайся медленно — минимум 2 секунды вниз\n"
             "• Цель: бёдра параллельно полу или ниже"),

            ("🔝  ДВИЖЕНИЕ ВВЕРХ",
             "• Толкайся пятками от пола\n"
             "• Колени не своди внутрь при подъёме\n"
             "• Выпрямляй ноги полностью в верхней точке\n"
             "• Не делай рывков — движение плавное"),

            ("🔴  ЧАСТЫЕ ОШИБКИ",
             "• Колени заваливаются внутрь (вальгус) — ОПАСНО!\n"
             "• Пятки отрываются от пола\n"
             "• Слишком сильный наклон корпуса вперёд\n"
             "• Неполная глубина — бёдра выше параллели\n"
             "• Слишком быстрый спуск"),

            ("✅  ПЕРЕД НАЧАЛОМ",
             "• Нажми СТАРТ и встань прямо\n"
             "• Подожди пока пройдёт калибровка (~2 сек)\n"
             "• После сигнала начинай приседать\n"
             "• Программа автоматически считает повторы и оценивает форму"),
        ]

        for header, text in sections:
            frame = QFrame()
            frame.setStyleSheet(
                "QFrame{background:#2d2d2d;border-radius:8px;padding:4px;}")
            fl = QVBoxLayout(frame)

            lbl_h = QLabel(header)
            lbl_h.setStyleSheet(
                "font-size:14px;font-weight:bold;color:#00adb5;padding:4px;")

            lbl_t = QLabel(text)
            lbl_t.setStyleSheet("color:#dddddd;font-size:13px;padding:4px;")
            lbl_t.setWordWrap(True)

            fl.addWidget(lbl_h)
            fl.addWidget(lbl_t)
            cl.addWidget(frame)

        scroll.setWidget(content)

        btn = QPushButton("← НАЗАД")
        btn.clicked.connect(on_back)

        layout.addWidget(title)
        layout.addWidget(scroll)
        layout.addWidget(btn)