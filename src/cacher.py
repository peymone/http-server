from datetime import datetime, timedelta
import sqlite3


class Cacher:
    def __init__(self, cache_expire_minutes: int, db_path: str, time_format: str) -> None:
        """Create database and load cache from it to dictionary"""

        # Initialize settings
        self.cache = dict()
        self.DB_PATH = db_path
        self.TIME_FORMAT = time_format
        self.EXPIRE_MINUTES = cache_expire_minutes

        # Create database and table
        self.db = sqlite3.connect(self.DB_PATH)
        self.cursor = self.db.cursor()
        self.create_table()  # Create table if not exists
        self.load_from_db()  # Load cache to memory and drop table

    def save(self, request_start_line: str, response_headers: bytes, response_body: bytes) -> None:
        expire_date = datetime.now() + timedelta(minutes=self.EXPIRE_MINUTES)
        self.cache[request_start_line] = response_headers, response_body, expire_date.strftime(self.TIME_FORMAT)

    def get(self, request_start_line: str) -> tuple[bytes, bytes, str] | None:
        cache = self.cache.get(request_start_line, None)
        if cache and not self.is_expired(cache[-1]):
            return cache

        return None

    def save_to_db(self) -> None:
        """Save cache dict to database and close connection"""

        save_list = [(key, values[0], values[1], values[2]) for key, values in self.cache.items()]
        self.cursor.executemany("INSERT INTO cache (request, header, body, expire) VALUES (?, ?, ?, ?)", save_list)
        self.db.commit()
        self.db.close()

    def load_from_db(self) -> None:
        """Get cache data from database and add it to dict"""

        # Get cache data from database
        self.cursor.execute("SELECT * FROM cache")

        if fetched_data := self.cursor.fetchall():

            # Add cache data from database to dict
            for data in fetched_data:
                request_start_line, headers, body, expire_date = data
                if not self.is_expired(expire_date):
                    self.cache[request_start_line] = headers, body, expire_date

            # Delete data from database
            self.cursor.execute("DROP TABLE cache")
            self.create_table()

    def create_table(self) -> None:
        """Create table 'cache' and commit changes"""

        self.cursor.execute("CREATE TABLE IF NOT EXISTS cache (request TEXT, header TEXT, body TEXT, expire TEXT)")
        self.db.commit()

    def is_expired(self, expire_date_string: str) -> bool:
        expire_date = datetime.strptime(expire_date_string, self.TIME_FORMAT)
        return True if datetime.now() >= expire_date else False
