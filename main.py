from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

app = Flask(__name__)

def clean_text(text):
    return re.sub(r'（.*?）', '', text).strip()

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    base_url = data.get("url")

    if not base_url:
        return jsonify({"error": "URLが指定されていません"}), 400

    all_data = []
    page = 1

    while True:
        page_url = f"{base_url}?page={page}" if page > 1 else base_url
        response = requests.get(page_url)
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.content, "html.parser")
        listings = soup.find_all("div", class_="dottable dottable--cassette")

        if not listings:
            break

        for prop in listings:
            try:
                location = prop.find("dt", string="所在地").find_next("dd").text.strip()
                price = prop.find("dt", class_="dottable-vm", string="販売価格").find_next("span", class_="dottable-value").text.strip()
                land = clean_text(prop.find("dt", string="土地面積").find_next("dd").text)
                building = clean_text(prop.find("dt", string="建物面積").find_next("dd").text)
                layout = prop.find("dt", string="間取り").find_next("dd").text.strip()
                age = prop.find("dt", string="築年月").find_next("dd").text.strip()

                data_entry = {
                    "所在地": location,
                    "販売価格": price,
                    "土地面積": land,
                    "建物面積": building,
                    "間取り": layout,
                    "築年月": age
                }

                all_data.append(data_entry)
            except AttributeError:
                continue  # 必須要素が欠けている物件はスキップ

        page += 1

    if not all_data:
        return jsonify({"error": "物件データが見つかりませんでした"}), 404

    df = pd.DataFrame(all_data)
    return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
