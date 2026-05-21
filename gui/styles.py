# filename: gui/styles.py
"""Кастомные стили оформления интерфейса (QSS)."""

STYLESHEET = """
QWidget { background-color:#1e1e1e; color:#fff; font-family:'Segoe UI',sans-serif; }
QGroupBox { border:1px solid #3d3d3d; border-radius:6px; margin-top:10px; font-weight:bold; }
QGroupBox::title { subcontrol-origin:margin; left:10px; padding:0 5px; color:#00adb5; }
QPushButton { background-color:#00adb5; color:white; border-radius:5px; padding:10px; font-weight:bold; }
QPushButton:hover { background-color:#00cece; }
QPushButton:disabled { background-color:#555; }
QPushButton#StopBtn { background-color:#c0392b; }
QPushButton#StopBtn:hover { background-color:#e74c3c; }
QLabel#StatsLabel { font-size:24px; font-weight:bold; color:#00adb5; }
QSpinBox { background-color:#2d2d2d; border:1px solid #3d3d3d; padding:5px; border-radius:4px; }
QTableWidget { background-color:#2d2d2d; gridline-color:#3d3d3d; border:none; }
QHeaderView::section { background-color:#1e1e1e; padding:4px; border:1px solid #3d3d3d; }
QProgressBar { border:1px solid #3d3d3d; border-radius:4px; background:#2d2d2d; text-align:center; }
QProgressBar::chunk { background-color:#00adb5; border-radius:3px; }
"""
