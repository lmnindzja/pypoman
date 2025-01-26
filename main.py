import sys
from PyQt5.QtWidgets import QApplication
from ui_main import ServiceManagerUI
from handlers import (
    load_data, open_disc, update_stats, on_selection_changed,
    restart_selected, stop_selected, start_selected, show_network_results
)


class ServiceManagerApp(ServiceManagerUI):
    def __init__(self):
        super().__init__()

        # Привязка обработчиков к кнопкам
        self.filter_button.clicked.connect(lambda: load_data(self))
        self.disc_button.clicked.connect(lambda: open_disc(self))
        self.restart_button.clicked.connect(lambda: restart_selected(self))
        self.stop_button.clicked.connect(lambda: stop_selected(self))
        self.start_button.clicked.connect(lambda: start_selected(self))
        self.network_button.clicked.connect(lambda: show_network_results(self))

        # Привязка событий таблицы
        self.table.selectionModel().selectionChanged.connect(lambda selected, deselected: on_selection_changed(self))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServiceManagerApp()
    window.show()
    sys.exit(app.exec_())
