import time

from rethinkdb import errors, r


class RethinkDBConnector:
    def __init__(self, host: str, port: int, db_name: str, table_name: str):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.table_name = table_name
        self.conn = None

    def connect(self):
        """Connects to the database and retries indefinitely in case of failure"""
        while self.conn is None:
            print("A connection attempt to the database has been initiated")
            try:
                print(f"Trying to connect with {self.host}:{self.port} ...")
                self.conn = r.connect(self.host, self.port, self.db_name)
                print("Attempt succeded. Connection established")
            except errors.ReqlDriverError:
                print("Attempt failed. Restarting...")
                time.sleep(5)

    def setup_database(self):
        """Creates the 'self.db_name' database and  'self.table_name' table. In case of them being already in existence does nothing."""
        if not self.conn:
            self.connect()

        try:
            print(f'Trying to create the "{self.db_name}" database...')
            r.db_create(self.db_name).run(self.conn)
            print(f"Database {self.db_name} created.")
        except r.ReqlOpFailedError:
            print(f"Database {self.db_name} already exists.")
            pass

        try:
            print(f"Trying to create the {self.table_name} table...")
            r.db("radar").table_create("flights").run(self.conn)
            print(f"Table {self.table_name} created.")
        except r.ReqlOpFailedError:
            print(f"Table {self.table_name} already exists.")
            pass

    def upsert_database(self, json_list: list):
        """It accepts a raw list and encapsulates the database storage implementation."""
        if not self.conn:
            self.connect()

        try:
            result = (
                r.table("flights").insert(json_list, conflict="update").run(self.conn)
            )
            print("Database updated.")
            return result
        except errors.ReqlDriverError:
            print("Connection lost during and upsert operation")
            self.conn = None
            return None

    def close(self):
        """Closing the connection"""
        if self.conn:
            self.conn.close()
            print("Closed the connection to the database")
