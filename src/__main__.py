# Python libraries
from configparser import ConfigParser
from argparse import ArgumentParser

# My modules
from src.server import HTTPServer
from src.proxy import Proxy
from src.logger import logger_config


def load_config() -> tuple[str, int, int, list, int]:
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", help="Server host", type=str, required=False)
    parser.add_argument("-P", "--port", help="Server port", type=int, required=False)
    parser.add_argument("-M", "--max", help="Max allowed connections", type=int, required=False)
    arguments = parser.parse_args()

    # Get default settings from config file
    config = ConfigParser()
    config.read("src/configurations/config.ini")

    # Reassign default settings with shell arguments if exists
    server_host = arguments.host if arguments.host else config.get("SERVER", "HOST")
    server_port = arguments.port if arguments.port else config.getint("SERVER", "PORT")
    max_connections = arguments.max if arguments.max else config.getint("SERVER", "MAX_CONNECTIONS")

    # Get max connection attempts for proxy
    proxy_max_con_attempts = config.getint("PROXY", "MAX_CON_ATTEMPTS")

    # Get clients list for balancer
    services = list()
    for client in config.items("SERVICES"):
        host, port = client[1].split()
        services.append((host, int(port)))

    return server_host, server_port, max_connections, services, proxy_max_con_attempts


def start() -> None:
    # Load configurations
    host, port, max_connections, services, proxy_max_con_attempts = load_config()
    logger = logger_config.get_logger()

    # Create client and server instances
    client = Proxy(services, proxy_max_con_attempts)
    server = HTTPServer(host, port, max_connections, client)

    # Log server staring message
    server_starting_message = f"Starting server on http://{host}:{port}"
    logger.info(server_starting_message)
    print("\n" + server_starting_message + "\n")

    # Start server
    server.start()


if __name__ == "__main__":
    start()
