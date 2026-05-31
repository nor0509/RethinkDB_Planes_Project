import os
import time
from datetime import datetime

from database import RethinkDBConnector
from opensky_api import OpenSkyClient

client = OpenSkyClient()
DB_HOST = os.getenv("DB_HOST", "localhost")

db = RethinkDBConnector(host=DB_HOST, port=28015, db_name="radar", table_name="flights")
db.setup_database()


def log(message):
    """Helper function to print standardized log messages with a timestamp to the console."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [INFO] {message}")


log("Starting flight producer loop...")

while True:
    """Main execution loop that periodically polls the OpenSky API and persists flight updates to the database."""
    flights_cleaned = client.get_flights()

    if flights_cleaned:
        log(f"Inserting {len(flights_cleaned)} flights into the database.")
        db.upsert_database(flights_cleaned)
    else:
        log("No flights data received or API error.")

    wait_time = 5 if client.is_authenticated() else 30
    log(f"Sleeping for {wait_time} seconds.")

    time.sleep(wait_time)
