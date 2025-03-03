from asyncio import AbstractEventLoop
from typing import Generator
import socket


class Proxy:
    def __init__(self, services: list[tuple[str, int]]):
        self.services = services
        self.ENCODING = "utf-8"
        self.BUFFER = 1024

    def balancer(self) -> Generator[tuple[str, int], None, None]:
        """Get service for connecting"""

        while True:
            for service in self.services:
                yield service

    async def send_request_to_service(self, decoded_request: str, event_loop: AbstractEventLoop) -> bytes | None:
        """Send request to remote service by TCP socket"""

        answer_from_service = None

        # Create TCP socket and send request to service
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            for try_counter, service in enumerate(self.balancer(), 1):
                try:
                    await event_loop.sock_connect(sock, service)  # Conenct to service
                    await event_loop.sock_sendall(sock, decoded_request.encode(self.ENCODING))  # Send request
                    answer_from_service = await event_loop.sock_recv(sock, self.BUFFER)  # Get response

                # Can't connect to service
                except ConnectionRefusedError:
                    pass
                except OSError:
                    pass

                try_counter += 1

                if answer_from_service is not None:  # Got answer from service
                    break

                if try_counter == len(self.services):  # All services is down
                    break

        return answer_from_service
