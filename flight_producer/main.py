import os
import time

import opensky_api
from database import RethinkDBConnector

DB_HOST = os.getenv("DB_HOST", "localhost")

db = RethinkDBConnector(host=DB_HOST, port=28015, db_name="radar", table_name="flights")
db.setup_database()

while True:
    flights_raw = opensky_api.get_flights()

    if flights_raw and flights_raw.get("states"):
        flights_cleaned = opensky_api.parse_flights(flights_raw["states"])

        db.upsert_database(flights_cleaned)

    time.sleep(10.5)
