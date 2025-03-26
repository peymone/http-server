# Python library
import ssl
import asyncio
from datetime import datetime

# My modules
from src.config import config
from src.logger import logger
from src.cacher import cacher
from src.proxy import Proxy
from src.parser import Parser, get_html_response


class Server:
    def __init__(self):
        self.clients = list()

    async def handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        # Get host and port for connected client
        host, port = writer.get_extra_info("peername")[:2]
        self.clients.append((host, port))

        try:
            # Get request from client
            request = await reader.read(config["buffer"])
            status_line, _ = Parser.parse_http_request(request)
            logger.info(f"Request from {host}:{port} was received: '{status_line}'")

            # Build response from statics
            if status_line in config["statics"]:
                with open(config["static_path"] + config["statics"][status_line], mode="r", encoding="utf-8") as html:
                    response = get_html_response(html.read(), status="OK")
                    writer.write(response.encode())

            # Build response from cache
            elif cahed_response := cacher.get(status_line):
                writer.write(cahed_response)

            # Build response from home page
            elif not config["services"]:
                with open(config["home_page"], mode="r", encoding="utf-8") as html:
                    response = get_html_response(html.read(), status="OK")
                    writer.write(response.encode())

            # Build response from service
            else:
                service_response = await Proxy.send_request_to_service(request, host, port)

                if service_response:
                    writer.write(service_response)
                    cacher.save(status_line, service_response)
                else:
                    # All services is down
                    with open(config["down_page"], mode="r", encoding="utf-8") as html:
                        response = get_html_response(html.read(), status="SERVICES_DOWN")
                        writer.write(response.encode())

            # Send response back and close socket
            logger.info(f"Sending response back to client {host}:{port}")
            await writer.drain()
            await asyncio.sleep(1)
            writer.close()
            await writer.wait_closed()

        except ConnectionResetError:
            pass

    async def start(self):
        # Create SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=config["cert_path"],
                                    keyfile=config["cert_key"], password=config["cert_pass"])

        # Create and run async server
        server = await asyncio.start_server(self.handler, config["host"], config["port"], ssl=ssl_context)
        async with server:
            await server.serve_forever()


def run():
    logger.debug("Server starting on https://{}:{}".format(config["host"], config["port"]))
    start_time = datetime.now()

    try:
        server = Server()
        asyncio.run(server.start())
    except KeyboardInterrupt:
        pass

    cacher.save_to_db()
    logger.debug("Server was stopped, working time: {}".format(datetime.now() - start_time))
