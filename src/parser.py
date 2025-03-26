from dataclasses import dataclass


class Parser:
    @classmethod
    def parse_http_request(cls, request: bytes) -> tuple[str, dict[str, str]]:
        """Parse http request into start line and headers dictionary"""

        headers = dict()
        decoded_request = request.decode()
        splited_request = decoded_request.splitlines()
        request_start_line = " ".join(splited_request[0].split()[:-1])

        for line in splited_request[1:-1]:
            key, value = line.split(":", maxsplit=1)
            headers[key] = value.strip()

        return request_start_line, headers


@dataclass
class Headers:
    OK_STATUS: str = "HTTP/1.1 200 OK\r\n"
    SERVICES_DOWN_STATUS: bytes = "HTTP/1.0 503 Bad\r\n"
    CONTENT_TYPE: str = "Content-Type: text/html; charset=utf-8\r\n"
    CLOSE_CONNECTION: str = "Connection: close\r\n\r\n"


def get_html_response(html_content: str, status: str) -> str:
    CONTENT_LENGTH = "Content-Length: {}\r\n".format(len(html_content))

    match status:
        case "OK":
            response = (
                Headers.OK_STATUS +
                Headers.CONTENT_TYPE +
                CONTENT_LENGTH +
                Headers.CLOSE_CONNECTION +
                html_content
            )
        case "SERVICES_DOWN":
            response = (
                Headers.SERVICES_DOWN_STATUS +
                Headers.CONTENT_TYPE +
                CONTENT_LENGTH +
                Headers.CLOSE_CONNECTION +
                html_content
            )

    return response
