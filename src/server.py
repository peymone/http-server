# Python libraries
from asyncio import get_event_loop, run as run_async
import socket

# My modules
from src.proxy import Proxy
from src.cacher import Cacher
from src.parser import Parser
from src.models import Headers
from src.logger import logger_config


# Initialize some classes
logger = logger_config.get_logger()
cacher = Cacher()
parser = Parser()


class HTTPServer:
    def __init__(self, host: str, port: int, max_connections: int, proxy: Proxy) -> None:
        """Configurate TCP socket for server"""

        self.proxy = proxy
        self.HOST = host
        self.PORT = port
        self.BUFFER = 1024
        self.connections = dict()
        self.MAX_CONNECTIONS = max_connections
        self.HOME_PAGE = "etc/home_page.html"

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

        while True:  # Receive data from client
            request = await self.event_loop.sock_recv(client_sock, self.BUFFER)

            # Client sends empty data when disconnecting - b''
            if request:
                logger.info(f"Request from {host}:{port} received")

                # Parse http request and get response from cache
                request_start_line, _ = parser.parse_http_request(request)
                cached_response = cacher.get(request_start_line)

                if cached_response:  # Send response from cache
                    await self.event_loop.sock_sendall(client_sock, cached_response[0])  # Headers
                    await self.event_loop.sock_sendall(client_sock, cached_response[1])  # Body
                    break

                if not self.proxy.services:  # Send home page if no services in config
                    with open(self.HOME_PAGE, mode="rb") as home_page:
                        await self.event_loop.sock_sendall(client_sock, Headers.OK)
                        await self.event_loop.sock_sendfile(client_sock, home_page)
                    break

                # Send request from client to servise
                service_response = await self.event_loop.create_task(
                    self.proxy.send_request_to_service(request, self.event_loop)
                )

                if service_response:  # Send service response to client
                    await self.event_loop.sock_sendall(client_sock, service_response[0])  # Headers
                    await self.event_loop.sock_sendall(client_sock, service_response[1])  # Body
                    cacher.save(request_start_line, *service_response)  # Cache response
                else:
                    await self.event_loop.sock_sendall(client_sock, Headers.SERVICES_DOWN)  # All services is down

                logger.debug("Sended response from service to client")
                break

        logger.info("Data handler for {}:{} was closed".format(host, port))

    def start(self) -> None:
        """Start accepting connections from clients"""

        try:  # Run AsyncIO event loop
            logger.debug("Starting accept connections")
            run_async(self.accept_connections())

        except KeyboardInterrupt:  # Close event loop and server socket
            self.event_loop.stop()
            self.sock.close()
            logger.debug("Server socket was closed")

            cacher.save_to_db()  # Save cache to database
