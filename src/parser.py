class Parser:
    def parse_http_request(self, request: bytes) -> tuple[str, dict[str, str]]:
        """Parse http request into start line and headers dictionary"""

        decoded_request = request.decode()
        parsing_lines = decoded_request.splitlines()
        headers = dict()

        headers["method"] = parsing_lines[0].split()[0]
        headers["path"] = parsing_lines[0].split()[1]
        headers["protocol"] = parsing_lines[0].split()[2]

        for line in parsing_lines[1:-1]:
            key, value = line.split(":", 1)
            headers[key] = value.strip()

        return parsing_lines[0], headers
