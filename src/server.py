# Python libraries
from asyncio import get_event_loop, run as run_async
import socket

# My modules
from src.proxy import Proxy
from src.logger import logger_config


# Get logger
logger = logger_config.get_logger()


class HTTPServer:
    def __init__(self, host: str, port: int, max_connections: int, proxy: Proxy) -> None:
        """Configurate TCP socket for server"""

        self.proxy = proxy
        self.HOST = host
        self.PORT = port
        self.BUFFER = 1024
        self.connections = dict()
        self.MAX_CONNECTIONS = max_connections

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket object
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow socker reuse
        self.sock.bind((self.HOST, self.PORT))  # Bind server address to socket
        self.sock.listen(self.MAX_CONNECTIONS)  # Enable listen mode
        self.sock.setblocking(False)  # For async usage

        logger.debug("Server socket was created")

    async def accept_connections(self) -> None:
        """Accept client connections and start data receiving"""

        # Create AsyncIO event loop for socket methods
        self.event_loop = get_event_loop()

        # Accept connection from clients
        while len(self.connections) < self.MAX_CONNECTIONS:
            client_sock, client_addr = await self.event_loop.sock_accept(self.sock)
            host, port = client_addr

            # Add client to connections dict
            self.connections[client_addr] = client_sock
            logger.info(f"Connection with {host}:{port} was established")

            # Create async event loop task for client communication
            self.event_loop.create_task(self.handle_connection(client_sock, host, port))

        logger.debug("Stopping accept connections")

    async def handle_connection(self, client_sock: socket, host: str, port: int) -> None:
        """Handle communication with specific client"""

        logger.info("Data handler for {}:{} was started".format(host, port))

        while True:
            # Receive data from client
            request = await self.event_loop.sock_recv(client_sock, self.BUFFER)

            # Client sends empty data when disconnecting - b''
            if request:
                # Receive data and log it
                decoded_request = request.decode()
                logger.info(f"Request from {host}:{port} received")
                logger.info(decoded_request)

                # Send request to service and get response
                service_response = await self.event_loop.create_task(
                    self.proxy.send_request_to_service(request, self.event_loop))

                logger.debug("Sending response from service to client")

                # Send response back to client if it exists
                if service_response:
                    await self.event_loop.sock_sendall(client_sock, service_response[0])  # Headers
                    await self.event_loop.sock_sendall(client_sock, service_response[1])  # Body
                else:
                    await self.event_loop.sock_sendall(client_sock, b"No data")

                break

        logger.info("Data handler for {}:{} was closed".format(host, port))

    def start(self) -> None:
        """Start accepting connections from clients"""

        try:
            # Run AsyncIO event loop and log it
            logger.debug("Starting accept connections")
            run_async(self.accept_connections())

        except KeyboardInterrupt:
            # Stop event loop and close server socket
            self.event_loop.stop()
            self.sock.close()

            logger.debug("Server socket was closed")
