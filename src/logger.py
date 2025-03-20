import logging


class LoggerConfig:
    def __init__(self, save_file_path: str, time_format: str) -> None:
        FILE_PATH = save_file_path
        TIME_FORMAT = time_format
        HANDLER_FORMAT = "{asctime} {levelname} {message}"

        # Create logger and formatter
        self.logger = logging.getLogger("logs")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(HANDLER_FORMAT, style="{", datefmt=TIME_FORMAT)

        # Setup file logger
        file_handler = logging.FileHandler(FILE_PATH, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Setup stream logger
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
