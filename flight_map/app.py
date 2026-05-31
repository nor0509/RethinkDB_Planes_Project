import json
import os

from flask import Flask, Response, render_template
from rethinkdb import r

app = Flask(__name__)
DB_HOST = os.getenv("DB_HOST", "localhost")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stream")
def stream():
    def event_stream():
        conn = r.connect(host=DB_HOST, port=28015, db="radar")

        cursor = r.table("flights").changes().run(conn)

        for change in cursor:
            new_val = change.get("new_val")
            if new_val and new_val.get("latitude") and new_val.get("longitude"):
                yield f"data: {json.dumps(new_val)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
