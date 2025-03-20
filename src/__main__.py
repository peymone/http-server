# Python libraries
from configparser import RawConfigParser
from argparse import ArgumentParser

# My modules
from src.logger import LoggerConfig
from src.server import HTTPServer
from src.cacher import Cacher
from src.proxy import Proxy


def load_config() -> dict:
    settings = dict()

    parser = ArgumentParser()
    parser.add_argument("-H", "--host", help="Server host", type=str, required=False)
    parser.add_argument("-P", "--port", help="Server port", type=int, required=False)
    parser.add_argument("-M", "--max", help="Max allowed connections", type=int, required=False)
    arguments = parser.parse_args()

    # Read config file
    config = RawConfigParser()
    config.read("etc/config.ini")

    # Reassign default settings for server from shell arguments
    settings["host"] = arguments.host if arguments.host else config.get("SERVER", "HOST")
    settings["port"] = arguments.port if arguments.port else config.getint("SERVER", "PORT")
    settings["max_con"] = arguments.max if arguments.max else config.getint("SERVER", "MAX_CONNECTIONS")

    # Get other settings from config
    settings["proxy_max_con_attempts"] = config.getint("PROXY", "MAX_CON_ATTEMPTS")
    settings["cache_expire_minutes"] = config.getint("CACHER", "EXPIRE_MINUTES")
    settings["cache_db_path"] = config.get("CACHER", "DB_PATH")
    settings["time_format"] = config.get("BASE", "TIME_FORMAT")
    settings["logs_path"] = config.get("LOGGER", "LOGS_PATH")
    settings["home_page"] = config.get("SERVER", "HOME_PAGE_PATH")
    settings["down_page"] = config.get("SERVER", "DOWN_PAGE_PATH")

    # Get clients list for balancer
    services = list()
    for client in config.items("SERVICES"):
        host, port = client[1].split()
        services.append((host, int(port)))

    settings["services"] = services

    return settings


def start() -> None:
    config = load_config()  # Load configurations

    # Create class instances
    logger_config = LoggerConfig(config["logs_path"], config["time_format"])
    cacher = Cacher(config["cache_expire_minutes"], config["cache_db_path"], config["time_format"])
    proxy = Proxy(config["services"], config["proxy_max_con_attempts"], logger_config.get_logger())

    # Create and start server
    server = HTTPServer(config["host"], config["port"], config["max_con"], logger_config.get_logger(), cacher, proxy,
                        config["home_page"], config["down_page"], config["time_format"])
    server.start()  # Start server
