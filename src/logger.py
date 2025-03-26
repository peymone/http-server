import logging
from src.config import config


class LoggerConfig:
    def __init__(self) -> None:
        HANDLER_FORMAT = "{asctime} {levelname} {message}"

        # Create logger and formatter
        self.logger = logging.getLogger("logs")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(HANDLER_FORMAT, style="{", datefmt=config["time_format"])

        # Setup file logger
        file_handler = logging.FileHandler(config["logs_path"], mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Setup stream logger
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)


logger = LoggerConfig().logger
