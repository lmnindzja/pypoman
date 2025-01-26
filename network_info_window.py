from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
from PyQt5.QtGui import QColor
import matplotlib.pyplot as plt
import networkx as nx

class NetworkInfoWindow(QDialog):
    def __init__(self, network_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Network Information")

        # Устанавливаем размеры окна
        self.resize(1200, 800)
        self.setWindowState(self.windowState() | 0x00000002)

        layout = QVBoxLayout(self)

        # Таблица для сетевой информации
        self.table = QTableWidget()
        self.table.setRowCount(len(network_data))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "State", "Local Address", "Local Host Name", "Local Port",
            "Remote Address", "Remote Host Name", "Remote Port"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)  # Включаем сортировку таблицы

        # Заполняем таблицу данными
        for row_idx, item in enumerate(network_data):
            for col_idx, key in enumerate(["State", "LocalAddress", "LocalHostName", "LocalPort", "RemoteAddress", "RemoteHostName", "RemotePort"]):
                value = item.get(key, "")
                if key == "State" and isinstance(value, dict) and "Value" in value:
                    value = value["Value"]  # Извлекаем текстовое значение из словаря

                cell_item = QTableWidgetItem(str(value))

                # Раскрашиваем строку в зависимости от состояния соединения
                if key == "State":
                    if value == "Established":
                        cell_item.setBackground(QColor("green"))
                        cell_item.setForeground(QColor("white"))
                    elif value == "Listen":
                        cell_item.setBackground(QColor("blue"))
                        cell_item.setForeground(QColor("white"))
                    elif value == "Closed":
                        cell_item.setBackground(QColor("red"))
                        cell_item.setForeground(QColor("white"))
                    else:
                        cell_item.setBackground(QColor("yellow"))
                        cell_item.setForeground(QColor("black"))

                self.table.setItem(row_idx, col_idx, cell_item)

        layout.addWidget(self.table)

        # Кнопка для генерации сетевой схемы
        self.graph_button = QPushButton("Сетевая схема")
        self.graph_button.clicked.connect(lambda: self.generate_network_graph(network_data))
        layout.addWidget(self.graph_button)

    def generate_network_graph(self, data):
        """Генерация и отображение сетевой схемы."""
        G = nx.Graph()

        for connection in data:
            local = connection.get("LocalAddress", "")
            remote = connection.get("RemoteAddress", "")
            if local and remote:
                G.add_edge(local, remote)

        plt.figure(figsize=(10, 8))
        nx.draw_networkx(G, with_labels=True, node_color="lightblue", edge_color="gray", font_size=10)
        plt.title("Сетевая схема")
        plt.show()
