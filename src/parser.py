from dataclasses import dataclass


class Parser:
    def parse_http_request(self, request: bytes) -> tuple[str, dict[str, str]]:
        """Parse http request into start line and headers dictionary"""

        headers = dict()
        decoded_request = request.decode()
        splited_request = decoded_request.splitlines()
        request_start_line = " ".join(splited_request[0].split()[:-1])

        for line in splited_request[1:-1]:
            key, value = line.split(":", maxsplit=1)
            headers[key] = value.strip()

        return request_start_line, headers


HTML_CONTENT = b"\nContent-Type: text/html\nConnection: close\n\n"


@dataclass
class Headers:
    OK: bytes = b"HTTP/1.0 200 OK" + HTML_CONTENT
    SERVICES_DOWN: bytes = b"HTTP/1.0 503 Bad" + HTML_CONTENT
