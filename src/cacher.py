class Cacher:
    def __init__(self) -> None:
        self.DATABASE = "etc/cache/cach.db"
        self.EXPIRE = None
        self.cache = dict()

    def save(self, request_start_line: str, response_headers: bytes, response_body: bytes):
        self.cache[request_start_line] = response_headers, response_body

    def get(self, request_start_line: str) -> tuple[bytes, bytes] | None:
        return self.cache.get(request_start_line, None)

    def save_to_db(self): pass

    def load_from_db(self): pass
