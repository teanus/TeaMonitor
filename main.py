import logging
import os
import socket
import sys

import psutil
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
                             QHBoxLayout, QMainWindow, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)

from logger import Logger


class ConnectionType:
    """Класс для определения типа сетевого соединения."""

    @staticmethod
    def get_type(connection) -> str:
        """Возвращает тип сетевого соединения на основе типа сокета.

        Args:
            connection: Объект сетевого соединения.

        Returns:
            str: Тип соединения (TCP, UDP или неизвестный).
        """
        if connection.type == socket.SOCK_STREAM:
            return "TCP"
        elif connection.type == socket.SOCK_DGRAM:
            return "UDP"
        else:
            return "Неизвестно"


class NetworkMonitorUI:
    """Класс для инициализации пользовательского интерфейса мониторинга сети."""

    def __init__(self) -> None:
        """Инициализирует приложение PyQt и отображает окно NetworkMonitor."""
        self.app = QApplication(sys.argv)
        self.monitor = NetworkMonitor()
        self.monitor.show()
        sys.exit(self.app.exec_())


class NetworkMonitor(QMainWindow):
    """Главный класс окна для приложения мониторинга сети."""

    def __init__(self) -> None:
        """Инициализирует окно приложения и устанавливает таймер обновления данных."""
        super().__init__()
        self.table_widget = None
        self.font_table = QFont("Montserrat", 10, QFont.Normal)
        self.menu_bar = None
        self.vertical_layout = None
        self.layout = None
        self.central_widget = None
        self.refresh_button = None
        self.logger = Logger()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.setInterval(1000)

    def init_ui(self) -> None:
        """Инициализирует пользовательский интерфейс приложения."""
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Сетевая активность компьютера")
        self.setGeometry(100, 100, 600, 800)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout()
        self.vertical_layout = QVBoxLayout()
        self.setup_menu()
        self.setup_table()

    def start_timer(self) -> None:
        """Запускает таймер для обновления данных по сетевой активности."""
        self.timer.start()

    def setup_menu(self) -> None:
        """Настройка меню приложения."""
        self.menu_bar = self.menuBar()
        options_menu = self.menu_bar.addMenu("Дополнительно")

        open_logs_action = QAction("Открыть логи", self)
        open_logs_action.triggered.connect(self.open_logs)
        options_menu.addAction(open_logs_action)

    def setup_table(self) -> None:
        """Настройка таблицы для отображения сетевой активности."""
        self.table_widget = QTableWidget()
        self.table_widget.setFont(self.font_table)
        self.table_widget.setMaximumWidth(550)
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(
            ["Название", "PID", "Айпи", "Порт", "Протокол"]
        )
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for col in range(self.table_widget.columnCount()):
            self.table_widget.setColumnWidth(col, 130)

        self.vertical_layout.addWidget(self.table_widget)

        self.refresh_button = QPushButton("Запустить")
        self.refresh_button.clicked.connect(self.start_timer)
        self.vertical_layout.addWidget(self.refresh_button, alignment=Qt.AlignHCenter)

        self.layout.addLayout(self.vertical_layout)
        self.central_widget.setLayout(self.layout)

    def refresh_data(self) -> None:
        """Обновляет данные о сетевой активности."""
        if not self.timer.isActive():
            return

        try:
            self.logger.log(logging.INFO, "Обновление данных о сети...")
            self.clear_table()
            network_connections = psutil.net_connections(kind="inet")
            self.table_widget.setRowCount(len(network_connections))

            for row, conn in enumerate(network_connections):
                if conn.pid:
                    try:
                        process = psutil.Process(conn.pid)
                        name_item = QTableWidgetItem(process.name())
                        pid_item = QTableWidgetItem(str(conn.pid))
                        protocol_item = QTableWidgetItem(
                            conn.laddr.ip if conn.laddr else ""
                        )
                        port_item = QTableWidgetItem(
                            str(conn.laddr.port) if conn.laddr else ""
                        )
                        type_item = QTableWidgetItem(ConnectionType.get_type(conn))

                        self.table_widget.setItem(row, 0, name_item)
                        self.table_widget.setItem(row, 1, pid_item)
                        self.table_widget.setItem(row, 2, protocol_item)
                        self.table_widget.setItem(row, 3, port_item)
                        self.table_widget.setItem(row, 4, type_item)

                        self.logger.log(
                            logging.INFO,
                            f"Соединение {row + 1}: "
                            f"Имя процесса: {process.name()}, "
                            f"PID: {conn.pid}, "
                            f"Протокол: {conn.laddr.ip if conn.laddr else ''}, "
                            f"Порт: {conn.laddr.port if conn.laddr else ''}, "
                            f"Тип соединения: {ConnectionType.get_type(conn)}",
                        )
                    except (
                            psutil.NoSuchProcess,
                            psutil.AccessDenied,
                            psutil.ZombieProcess,
                    ) as e:
                        self.logger.log(
                            logging.ERROR, f"Ошибка при обработке соединения: {e}"
                        )
        except Exception as e:
            self.logger.log(
                logging.ERROR, f"Произошла ошибка при обновлении данных: {e}"
            )

    def clear_table(self) -> None:
        """Очищает таблицу сетевых соединений."""
        self.table_widget.setRowCount(0)

    @staticmethod
    def open_logs() -> None | str:
        """Открывает файл журнала сетевой активности."""
        file_path = "tea_monitor.log"
        try:
            os.startfile(file_path)
        except FileNotFoundError:
            return f"Файл {file_path} не найден."

    @staticmethod
    def clear_file_log() -> None:
        """Очищает файл журнала сетевой активности"""
        with open("tea_monitor.log", "w") as file:
            file.write(" ")


if __name__ == "__main__":
    NetworkMonitorUI()
