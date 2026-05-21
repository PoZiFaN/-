# filename: gui/navigation_controller.py
from PyQt6.QtWidgets import QStackedWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gui.main_window import MainWindow

# Константы индексов страниц
PAGE_VIDEO = 0
PAGE_RESULTS = 1
PAGE_HISTORY = 2
PAGE_INSTRUCTION = 3


class NavigationController:
    """
    Контроллер навигации и координации состояния интерфейса.
    Инкапсулирует логику переходов между страницами стека.
    """
    def __init__(self, main_window: "MainWindow"):
        self.main_window = main_window

    def go_to_video(self):
        """Переключает стек на отображение видеопотока тренировки."""
        self.main_window.stack.setCurrentIndex(PAGE_VIDEO)

    def go_to_results(self, session):
        """Обрабатывает завершение сессии, сохраняет данные и показывает итоги."""
        self.main_window._reset_buttons()
        history = session.rep_history
        
        from storage.csv_reader import get_summary
        from storage.csv_writer import save_session
        
        summary = get_summary(history)
        saved = save_session(history)
        
        self.main_window.results_page.populate(history, summary, saved)
        self.main_window.stack.setCurrentIndex(PAGE_RESULTS)

    def go_to_history(self):
        """Загружает архив файлов CSV из хранилища и открывает историю."""
        from storage.csv_reader import load_all
        self.main_window.history_page.populate(load_all())
        self.main_window.stack.setCurrentIndex(PAGE_HISTORY)

    def go_to_instruction(self):
        """Переключает стек на интерактивную страницу с инструкциями."""
        self.main_window.stack.setCurrentIndex(PAGE_INSTRUCTION)
