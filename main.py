import json
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATA_FILE = Path(__file__).parent / "data.json"


def load_data():
    return json.loads(DATA_FILE.read_text())


def save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        form = request.form
        sections = []
        section_idx = 0

        while f"s{section_idx}_heading" in form:
            section = {
                "heading": form[f"s{section_idx}_heading"],
                "entries": [],
            }
            entry_idx = 0
            while f"s{section_idx}_e{entry_idx}_title" in form:
                p = f"s{section_idx}_e{entry_idx}"
                meta_raw = form.get(f"{p}_meta", "")
                meta = [l.strip() for l in meta_raw.splitlines() if l.strip()]

                entry = {
                    "title": form[f"{p}_title"],
                    "subtitle": form.get(f"{p}_subtitle", ""),
                    "meta": meta,
                    "logo": {
                        "url": form.get(f"{p}_logo_url", "#"),
                        "src": form.get(f"{p}_logo_src", ""),
                        "alt": form.get(f"{p}_logo_alt", ""),
                    },
                }
                desc = form.get(f"{p}_description", "").strip()
                if desc:
                    entry["description"] = desc
                skills = form.get(f"{p}_skills", "").strip()
                if skills:
                    entry["skills"] = skills

                section["entries"].append(entry)
                entry_idx += 1

            sections.append(section)
            section_idx += 1

        save_data({"sections": sections})
        return redirect(url_for("index"))

    data = load_data()
    return render_template("index.html", sections=data["sections"])


if __name__ == "__main__":
    app.run(debug=True, port=5001)
