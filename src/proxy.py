# Python libraries
from asyncio import AbstractEventLoop
from typing import Generator
from logging import Logger
import socket


class Proxy:
    def __init__(self, services: list[tuple[str, int]], max_con_attempts: int, logger: Logger):
        self.services = services
        self.logger = logger
        self.BUFFER = 1024
        self.MAX_CONNECTION_ATTEMPTS = max_con_attempts

    def balancer(self) -> Generator[tuple[str, int], None, None]:
        """Get service for connecting"""

        counter = 0
        while counter < self.MAX_CONNECTION_ATTEMPTS:
            for service in self.services:
                yield service
            counter += 1

    async def send_request_to_service(self, encoded_request: bytes, event_loop: AbstractEventLoop) -> tuple[bytes, bytes] | None:
        """Send request to remote service by TCP socket"""

        headers = None

        # Create TCP socket and send request to service
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            for service in self.balancer():
                try:
                    # Connect to service and send request
                    self.logger.debug("Send request from client to service on {}:{}".format(*service))
                    await event_loop.sock_connect(sock, service)
                    await event_loop.sock_sendall(sock, encoded_request)

                    # Receive response from service
                    headers = await event_loop.sock_recv(sock, self.BUFFER)
                    body = await event_loop.sock_recv(sock, self.BUFFER)

                # Can't connect to service
                except ConnectionRefusedError:
                    pass
                except OSError:
                    pass

                # Got non empty answer from service
                if headers is not None:
                    break

        # Return response from service
        if headers:
            self.logger.debug("Receive response from service on {}:{}".format(*service))
            return headers, body
        else:
            self.logger.debug("No data from service was received - all services is down")
            return None
