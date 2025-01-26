from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QWidget, QHeaderView, QCheckBox
)


class ServiceManagerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Host Info")
        self.setGeometry(100, 100, 1400, 800)

        # Разворачиваем окно на весь экран
        self.showMaximized()

        # Основной виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)

        # Верхняя панель поиска и фильтрации
        top_panel = QHBoxLayout()
        self.label_search = QLabel("Введите маску имени хоста для поиска:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Place hostname here")
        self.search_mask_label = QLabel("*")
        self.filter_button = QPushButton("OK")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Отфильтруйте результаты")
        self.demo_mode_checkbox = QCheckBox("Демо режим")       

        top_panel.addWidget(self.label_search)
        top_panel.addWidget(self.search_input)
        top_panel.addWidget(self.search_mask_label)
        top_panel.addWidget(self.filter_button)
        top_panel.addWidget(self.filter_input)
        top_panel.addWidget(self.demo_mode_checkbox)
        main_layout.addLayout(top_panel)
        

        # Таблица результатов
        self.table = QTableWidget()
        self.table.setRowCount(0)
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            "Server", "Port", "Type", "Name", "Version", "State", "Pid", "User", "StartTime", "BootTime", "RMQ_conn_count"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        self.table.setSortingEnabled(True)

        # Устанавливаем стратегию масштабирования столбцов
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        # Нижняя панель статистики
        stats_panel = QHBoxLayout()
        self.stats_label = QLabel("Выделено строк: 0 / Всего строк: 0 / Видимых строк: 0")
        self.stats_label.setStyleSheet("color: red;")
        stats_panel.addWidget(self.stats_label)
        main_layout.addLayout(stats_panel)

        # Нижняя панель кнопок
        buttons_panel = QHBoxLayout()
        self.restart_button = QPushButton("restart Selected")
        self.stop_button = QPushButton("Stop Selected")
        self.start_button = QPushButton("Start Selected")
        self.disc_button = QPushButton("Disc")
        self.network_button = QPushButton("Network")
        self.zabbix_button = QPushButton("Zabbix")

        buttons_panel.addWidget(self.restart_button)
        buttons_panel.addWidget(self.stop_button)
        buttons_panel.addWidget(self.start_button)
        buttons_panel.addWidget(self.disc_button)
        buttons_panel.addWidget(self.network_button)
        buttons_panel.addWidget(self.zabbix_button)

        main_layout.addLayout(buttons_panel)
