from configparser import ConfigParser
from argparse import ArgumentParser

from src.server import HTTPServer
from src.proxy import Proxy


def load_config() -> tuple[str, int, int, list]:
    parser = ArgumentParser()
    parser.add_argument("-H", "--host", help="Enter server host", type=str, required=False)
    parser.add_argument("-P", "--port", help="Enter server port", type=int, required=False)
    parser.add_argument("-M", "--max", help="Enter max connections allowed", type=int, required=False)
    arguments = parser.parse_args()

    # Get default settings from config file
    config = ConfigParser()
    config.read("src/configurations/config.ini")

    # Reassign default settings with shell arguments if exists
    server_host = arguments.host if arguments.host else config.get("SERVER", "HOST")
    server_port = arguments.port if arguments.port else config.getint("SERVER", "PORT")
    max_connections = arguments.max if arguments.max else config.getint("SERVER", "MAX_CONNECTIONS")

    # Get clients list for balancer
    services = list()
    for client in config.items("SERVICES"):
        host, port = client[1].split()
        services.append((host, int(port)))

    return server_host, server_port, max_connections, services


def start() -> None:
    host, port, max_connections, services = load_config()
    client = Proxy(services)
    server = HTTPServer(host, port, max_connections, client)

    print(f"\nStarting server on http://{host}:{port}\n")
    server.start()


if __name__ == "__main__":
    start()
