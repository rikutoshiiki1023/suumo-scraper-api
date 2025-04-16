from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

from scraping.area_old_houses import parse_area_old_houses
from scraping.area_old_apartments import parse_area_old_apartments
from scraping.client_old_houses import parse_client_old_houses
from scraping.client_old_apartments import parse_client_old_apartments

app = Flask(__name__)

@app.route("/process", methods=["POST"])
def process():
    content = request.json
    url = content.get("url")
    mode = content.get("mode")  # 'area_old_houses', 'area_old_apartments', etc.

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        if mode == "area_old_houses":
            result = parse_area_old_houses(soup)
        elif mode == "area_old_apartments":
            result = parse_area_old_apartments(soup)
        elif mode == "client_old_houses":
            result = parse_client_old_houses(soup)
        elif mode == "client_old_apartments":
            result = parse_client_old_apartments(soup)
        else:
            return jsonify({"error": "Invalid mode"}), 400

        return jsonify({"data": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
