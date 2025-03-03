from asyncio import get_event_loop, run as run_async
import socket

from src.proxy import Proxy


class HTTPServer:
    def __init__(self, host: str, port: int, max_connections: int, proxy: Proxy) -> None:
        """Configurate TCP socket for server"""

        self.proxy = proxy
        self.HOST = host
        self.PORT = port
        self.BUFFER = 1024
        self.connections = list()
        self.MAX_CONNECTIONS = max_connections

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket object
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow socker reuse
        self.sock.bind((self.HOST, self.PORT))  # Bind server address to socket
        self.sock.listen(self.MAX_CONNECTIONS)  # Enable listen mode
        self.sock.setblocking(False)  # For async usage

    async def accept_connections(self) -> None:
        """Accept client connections and start data receiving"""

        self.event_loop = get_event_loop()  # Event loop for async socket methods

        while len(self.connections) < self.MAX_CONNECTIONS:
            client_sock, client_addr = await self.event_loop.sock_accept(self.sock)  # Accept connection from client
            self.connections.append((client_addr, client_sock))
            self.event_loop.create_task(self.handle_connection(client_sock))  # Async task for client communication

    async def handle_connection(self, client_sock: socket) -> None:
        """Handle communication with specific client"""

        while True:
            request = await self.event_loop.sock_recv(client_sock, self.BUFFER)  # Receive data from client

            if request:  # Client send b'' when disconnecting
                decoded_request = request.decode()
                print(decoded_request)

                # Send request to service and get response
                service_response = await self.event_loop.create_task(
                    self.proxy.send_request_to_service(request, self.event_loop))

                # Send response back to client
                await self.event_loop.sock_sendall(client_sock, service_response[0])  # Headers
                await self.event_loop.sock_sendall(client_sock, service_response[1])  # Body

                break

    def start(self) -> None:
        """Start accepting connections from clients"""

        try:
            run_async(self.accept_connections())  # Run asyncio event loop
        except KeyboardInterrupt:
            self.event_loop.stop()  # Stop event loop - break sock_accept
            self.sock.close()  # Close server socket
