# Python libraries
from typing import Generator
import asyncio
import socket

# My modules
from src.config import config
from src.logger import logger


class Proxy:
    @classmethod
    def balancer(self) -> Generator[tuple[str, int], None, None]:
        """Get service for connecting"""

        counter = 0
        while counter < config["proxy_con_attempts"]:
            for host, port in config["services"].items():
                yield host, port
            counter += 1

    @classmethod
    async def send_request_to_service(self, request: bytes, host: str, port: int):
        """Send request to remote service by TCP socket"""

        event_loop = asyncio.get_running_loop()
        headers = body = None

        # Create TCP socket and send request to service
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            for service in self.balancer():
                try:
                    # Connect to service and send request
                    logger.debug("Sending request from {}:{} to service {}:{}".format(host, port, *service))
                    await event_loop.sock_connect(sock, service)
                    await event_loop.sock_sendall(sock, request)

                    # Receive response from service
                    headers = await event_loop.sock_recv(sock, config["buffer"])
                    body = await event_loop.sock_recv(sock, config["buffer"])

               # Unable to connect to service
                except ConnectionRefusedError:
                    pass
                except OSError:
                    pass

        # Return service response back to server
        if headers or body:
            logger.debug("Received response from service {}:{}".format(*service))
            return headers + body
        else:
            logger.debug("No data received from service (all services is down)")
            return None
