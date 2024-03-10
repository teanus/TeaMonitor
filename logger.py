import logging


class Logger:
    """
    Класс для ведения журнала сетевой активности компьютера TeaMonitor.
    """

    def __init__(self, log_file="tea_monitor.log"):
        """
        Инициализирует объект Logger с указанным файлом журнала.

        Аргументы:
            log_file (str): Имя файла журнала. По умолчанию 'tea_monitor.log'.
        """
        self.log_file = log_file

        logging.basicConfig(
            filename=self.log_file,
            level=logging.DEBUG,
            format="%(asctime)s - TeaMonitor Computer Network Activity -%(levelname)s - %(message)s",
        )

    @staticmethod
    def log(level, message):
        """
        Регистрирует сообщение с указанным уровнем журналирования.

        Аргументы:
            level (int): Уровень журналирования.
            message (str): Сообщение для регистрации.
        """
        logging.log(level, message)


if __name__ == "__main__":
    logger = Logger()
    logger.log(logging.INFO, "Логирование сетевой активности компьютера включено")
