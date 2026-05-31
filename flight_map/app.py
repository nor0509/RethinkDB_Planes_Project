import json
import os
from datetime import datetime

from flask import Flask, Response, render_template
from rethinkdb import r

app = Flask(__name__)
DB_HOST = os.getenv("DB_HOST", "localhost")


@app.route("/")
def index():
    """Serves the main dashboard page for the flight radar visualization."""
    return render_template("index.html")


@app.route("/stream")
def stream():
    """
    Establishes a Server-Sent Events (SSE) stream that pushes real-time
    flight updates from the RethinkDB changefeed to the web client.
    """

    def event_stream():
        conn = r.connect(host=DB_HOST, port=28015, db="radar")
        cursor = r.table("flights").changes(include_initial=True).run(conn)

        for change in cursor:
            new_val = change.get("new_val")
            if new_val and new_val.get("latitude") and new_val.get("longitude"):
                yield f"data: {json.dumps(new_val)}\n\n"
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(
                    f"[{timestamp}] [INFO] Streaming update for: {new_val.get('callsign', 'Unknown')}",
                    flush=True,
                )

    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
