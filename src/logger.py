import logging


class LoggerConfig:
    def __init__(self, save_file_path: str, time_format: str) -> None:
        FILE_PATH = save_file_path
        TIME_FORMAT = time_format
        LOGGING_LEVEL = "DEBUG"
        HANDLER_FORMAT = "{asctime} {levelname} {message}"

        # Create logger
        self.logger = logging.getLogger("logs")

        # Create handler and formatter for logger
        handler = logging.FileHandler(FILE_PATH, mode="a", encoding="utf-8")
        formatter = logging.Formatter(HANDLER_FORMAT, style="{", datefmt=TIME_FORMAT)

        # Set handler and formatter to logger
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Set logger level
        self.logger.setLevel(LOGGING_LEVEL)

    def get_logger(self) -> logging.Logger:
        return self.logger
