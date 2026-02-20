import requests
from flask import Flask, send_file, request, Response
from pathlib import Path

app = Flask(__name__, static_folder=None)
ROOT = Path(__file__).parent


@app.route("/")
def index():
    return send_file(ROOT / "index.html")


@app.route("/logo")
def logo_proxy():
    domain = request.args.get("d", "")
    if not domain:
        return "missing domain", 400
    try:
        r = requests.get(f"https://logo.uplead.com/{domain}", timeout=5)
        return Response(r.content, content_type=r.headers.get("Content-Type", "image/png"))
    except Exception:
        return "failed", 502


if __name__ == "__main__":
    app.run(debug=True, port=5001)
