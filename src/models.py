from dataclasses import dataclass


HTML_CONTENT = b"\nContent-Type: text/html\nConnection: close\n\n"


@dataclass
class Headers:
    OK: bytes = b"HTTP/1.0 200 OK" + HTML_CONTENT
    SERVICES_DOWN: bytes = b"HTTP/1.0 503 Bad" + HTML_CONTENT
