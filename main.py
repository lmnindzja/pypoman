import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QStatusBar
from ui_main import ServiceManagerUI
from handlers import (
    load_data, open_disc, update_stats, on_selection_changed,
    restart_selected, stop_selected, start_selected, show_network_results
)


class ServiceManagerApp(ServiceManagerUI):
    def __init__(self):
        super().__init__()

        # Создание меню
        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)

        # Меню "Файл"
        file_menu = QMenu("Файл", self)
        self.menu_bar.addMenu(file_menu)

        # Добавление действий в меню "Файл"
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Опции"
        options_menu = QMenu("Опции", self)
        self.menu_bar.addMenu(options_menu)

        demo_mode_action = QAction("Включить демо режим", self, checkable=True)
        demo_mode_action.setChecked(False)
        demo_mode_action.triggered.connect(lambda: self.toggle_demo_mode(demo_mode_action.isChecked()))
        options_menu.addAction(demo_mode_action)

        # Создание статусной строки
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")

        # Привязка обработчиков к кнопкам
        self.filter_button.clicked.connect(lambda: load_data(self))
        self.disc_button.clicked.connect(lambda: open_disc(self))
        self.restart_button.clicked.connect(lambda: restart_selected(self))
        self.stop_button.clicked.connect(lambda: stop_selected(self))
        self.start_button.clicked.connect(lambda: start_selected(self))
        self.network_button.clicked.connect(lambda: show_network_results(self))

        # Привязка событий таблицы
        self.table.selectionModel().selectionChanged.connect(lambda selected, deselected: on_selection_changed(self))

    def toggle_demo_mode(self, enabled):
        """Переключение демо режима."""
        self.demo_mode_checkbox.setChecked(enabled)
        if enabled:
            self.status_bar.showMessage("Демо режим включён")
        else:
            self.status_bar.showMessage("Демо режим выключен")


def apply_styles(app):
    """Применение глобальных стилей для приложения."""
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QPushButton {
            background-color: #0078d4;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        QPushButton:pressed {
            background-color: #003f74;
        }
        QLineEdit {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px;
        }
        QTableWidget {
            background-color: white;
            gridline-color: #ccc;
        }
        QTableWidget QHeaderView::section {
            background-color: #e1e1e1;
            padding: 4px;
            border: 1px solid #d6d6d6;
        }
        QStatusBar {
            background-color: #f1f1f1;
            color: #333;
        }
    """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_styles(app)
    window = ServiceManagerApp()
    window.show()
    sys.exit(app.exec_())