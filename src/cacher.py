# Python library
from datetime import datetime, timedelta
import sqlite3

# My modules
from src.config import config
from src.logger import logger


class Cacher:
    def __init__(self) -> None:
        """Create database and load cache from it to dictionary"""

        self.cache = dict()

        # Create database and table
        self.db = sqlite3.connect(config["cache_path"])
        self.cursor = self.db.cursor()
        self.create_table()  # Create table if not exists
        self.load_from_db()  # Load cache to memory and drop table

    def save(self, request: str, response: bytes) -> None:
        """Save cache in memory"""

        logger.debug(f"Saving response to cahce for: '{request}'")
        expire_date = datetime.now() + timedelta(minutes=config["cache_expire_minutes"])
        self.cache[request] = response, expire_date.strftime(config["time_format"])

    def get(self, request: str) -> tuple[bytes, bytes, str] | None:
        """Get cache data by request start line"""

        cache = self.cache.get(request, None)
        if cache and not self.is_expired(cache[-1]):
            logger.debug(f"Got response from cache for request: '{request}'")
            return cache[0]

        return None

    def save_to_db(self) -> None:
        """Save cache from memory to database"""

        save_list = [(key, values[0], values[1]) for key, values in self.cache.items()]
        self.cursor.executemany("INSERT INTO cache (request, response, expire) VALUES (?, ?, ?)", save_list)
        self.db.commit()
        self.db.close()

    def load_from_db(self) -> None:
        """Get cache data from database and add it to dict"""

        # Get cache data from database
        self.cursor.execute("SELECT * FROM cache")

        if fetched_data := self.cursor.fetchall():

            # Add cache data from database to dict
            for data in fetched_data:
                request, response, expire_date = data
                if not self.is_expired(expire_date):
                    self.cache[request] = response, expire_date

            # Delete data from database
            self.cursor.execute("DROP TABLE cache")
            self.create_table()

    def create_table(self) -> None:
        """Create table 'cache' and commit changes"""

        self.cursor.execute("CREATE TABLE IF NOT EXISTS cache (request TEXT, response TEXT, expire TEXT)")
        self.db.commit()

    def is_expired(self, expire_date_string: str) -> bool:
        expire_date = datetime.strptime(expire_date_string, config["time_format"])
        return True if datetime.now() >= expire_date else False


cacher = Cacher()
