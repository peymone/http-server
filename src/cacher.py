import sqlite3


class Cacher:
    def __init__(self) -> None:
        """Create database and load cache from it to dictionary"""

        self.DB_PATH = "etc/cache.db"
        self.EXPIRE = None
        self.cache = dict()

        # Create database and table
        self.db = sqlite3.connect(self.DB_PATH)
        self.cursor = self.db.cursor()
        self.create_table()  # Create table if not exists
        self.load_from_db()  # Load cache to memory and drop table

    def save(self, request_start_line: str, response_headers: bytes, response_body: bytes):
        self.cache[request_start_line] = response_headers, response_body

    def get(self, request_start_line: str) -> tuple[bytes, bytes] | None:
        return self.cache.get(request_start_line, None)

    def save_to_db(self):
        """Save cache dict to database and close connection"""

        save_list = [(key, value[0], value[1]) for key, value in self.cache.items()]
        self.cursor.executemany("INSERT INTO cache (request, header, body) VALUES (?, ?, ?)", save_list)
        self.db.commit()
        self.db.close()

    def load_from_db(self):
        """Get cache data from database and add it to dict"""

        # Get cache data from database
        self.cursor.execute("SELECT * FROM cache")

        if fetched_data := self.cursor.fetchall():

            # Add cache data from database to dict
            for data in fetched_data:
                request_start_line, headers, body = data
                self.cache[request_start_line] = headers, body

            # Delete data from database
            self.cursor.execute("DROP TABLE cache")
            self.create_table()

    def create_table(self):
        """Create table 'cache' and commit changes"""

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS cache
                            (request text, header text, body text)
                            """)
        self.db.commit()
