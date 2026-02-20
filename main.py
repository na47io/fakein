import json
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data.json"


def load_data():
    return json.loads(DATA_FILE.read_text())


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))


@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", sections=data["sections"])


if __name__ == "__main__":
    app.run(debug=True, port=5001)
