# Python libraries
from asyncio import get_event_loop, run as run_async
import socket

# My modules
from src.proxy import Proxy
from src.cacher import Cacher
from src.parser import Parser, Headers
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
        self.HOME_PAGE = "etc/templates/home_page.html"
        self.DOWN_PAGE = "etc/templates/services_down.html"

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create socket object
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow socker reuse
        self.sock.bind((self.HOST, self.PORT))  # Bind server address to socket
        self.sock.listen(self.MAX_CONNECTIONS)  # Enable listen mode
        self.sock.setblocking(False)  # For async usage

    async def accept_connections(self) -> None:
        """Accept client connections and start data receiving"""

        self.event_loop = get_event_loop()  # Event loop for socket communication

        # Accept connection from client
        while len(self.connections) < self.MAX_CONNECTIONS:
            client_sock, client_addr = await self.event_loop.sock_accept(self.sock)
            self.connections[client_addr] = client_sock  # Add client to conenction dict

            # Create async event loop task for client communication
            self.event_loop.create_task(self.handle_connection(client_sock, *client_addr))

    async def handle_connection(self, client_sock: socket, host: str, port: int) -> None:
        """Handle communication with specific client"""

        request = await self.event_loop.sock_recv(client_sock, self.BUFFER)  # Receive data from client

        if request:  # Client sends empty data when disconnecting

            # Parse http request and log it
            request_start_line, headers = parser.parse_http_request(request)
            logger.info(f"Request from {host}:{port} received: {request_start_line}")

            # Send response from cache if exists
            if cached_response := cacher.get(request_start_line):
                await self.event_loop.sock_sendall(client_sock, cached_response[0])  # Headers
                await self.event_loop.sock_sendall(client_sock, cached_response[1])  # Body

            # Send home page if no services listed in config
            elif not self.proxy.services:
                with open(self.HOME_PAGE, mode="rb") as home_page:
                    await self.event_loop.sock_sendall(client_sock, Headers.OK)  # Headers
                    await self.event_loop.sock_sendfile(client_sock, home_page)  # Body

            # Send response from services
            else:
                # Send request from client to service
                service_response = await self.event_loop.create_task(self.proxy.send_request_to_service(request, self.event_loop))

                if service_response:  # Send service response back to client
                    await self.event_loop.sock_sendall(client_sock, service_response[0])  # Headers
                    await self.event_loop.sock_sendall(client_sock, service_response[1])  # Body
                    cacher.save(request_start_line, *service_response)  # Cache response
                else:
                    # Send down page - all services is down
                    with open(self.DOWN_PAGE, mode="rb") as down_page:
                        await self.event_loop.sock_sendall(client_sock, Headers.SERVICES_DOWN)  # Headers
                        await self.event_loop.sock_sendfile(client_sock, down_page)  # Body

                logger.debug(f"Response from service sended back to client on {host}:{port}")

    def start(self) -> None:
        """Start accepting connections from clients"""

        try:  # Run AsyncIO event loop
            run_async(self.accept_connections())

        except KeyboardInterrupt:  # Close event loop and socket, save cache to db
            self.event_loop.stop()
            self.sock.close()
            cacher.save_to_db()
