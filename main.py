# filename: main.py
import os
import sys
import logging

# ЖЕСТКАЯ ОПТИМИЗАЦИЯ ПОД AMD RYZEN 5 3500U (4 физических ядра)
os.environ["KMP_DUPLICATE_LIB_OK"]         = "TRUE"
os.environ["OMP_NUM_THREADS"]              = "4"  # Строго 4 потока, чтобы не вешать ОС
os.environ["MKL_NUM_THREADS"]              = "4"
os.environ["MKL_THREADING_LAYER"]          = "GNU"
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.styles import STYLESHEET

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
