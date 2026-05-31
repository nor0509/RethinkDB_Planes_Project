import time
from datetime import datetime

from rethinkdb import errors, r


class RethinkDBConnector:
    def __init__(self, host: str, port: int, db_name: str, table_name: str):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.table_name = table_name
        self.conn = None

    def _log(self, message):
        """Helper method to print formatted log messages with a timestamp and severity level."""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] [INFO] {message}")

    def connect(self):
        """Handles the persistent database connection attempt, retrying every 5 seconds until successful."""
        while self.conn is None:
            self._log("A connection attempt to the database has been initiated")
            try:
                self._log(f"Trying to connect with {self.host}:{self.port} ...")
                self.conn = r.connect(self.host, self.port, self.db_name)
                self._log("Attempt succeeded. Connection established")
            except errors.ReqlDriverError:
                self._log("Attempt failed. Restarting...")
                time.sleep(5)

    def setup_database(self):
        """Ensures the required database and table structure exists, creating them if necessary."""
        if not self.conn:
            self.connect()
        try:
            self._log(f'Trying to create the "{self.db_name}" database...')
            r.db_create(self.db_name).run(self.conn)
            self._log(f"Database {self.db_name} created.")
        except r.ReqlOpFailedError:
            self._log(f"Database {self.db_name} already exists.")

        try:
            self._log(f"Trying to create the {self.table_name} table...")
            r.db("radar").table_create("flights").run(self.conn)
            self._log(f"Table {self.table_name} created.")
        except r.ReqlOpFailedError:
            self._log(f"Table {self.table_name} already exists.")

    def upsert_database(self, json_list):
        """Performs a bulk upsert of flight data into the database, with retry logic for handling initialization delays."""
        max_retries = 5
        for attempt in range(max_retries):
            try:
                r.table("flights").insert(json_list, conflict="update").run(self.conn)
                self._log("Data inserted successfully")
                return
            except errors.ReqlOpFailedError:
                self._log(
                    f"Database not ready, retrying... ({attempt + 1}/{max_retries})"
                )
                time.sleep(5)
            except Exception as e:
                self._log(f"Unexpected error: {e}")
                break
