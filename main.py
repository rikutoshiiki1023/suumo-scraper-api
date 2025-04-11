from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

app = Flask(__name__)

def clean_text(text):
    return re.sub(r'（.*?）', '', text).strip()

def scrape_suumo_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    except:
        return None

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    base_url = data.get("url")
    
    if not base_url:
        return jsonify({"error": "URLが指定されていません"}), 400

    page = 1
    all_data = []

    while True:
        page_url = base_url if page == 1 else f"{base_url}?page={page}"
        soup = scrape_suumo_page(page_url)
        if not soup:
            break

        property_units = soup.find_all(class_=re.compile('^property_unit'))
        if not property_units:
            break  # ページにデータがなければ終了

        for prop in property_units:
            try:
                location = prop.find("dt", text="所在地").find_next("dd").text.strip()
                price = prop.find("dt", class_="dottable-vm", text="販売価格").find_next("span", class_="dottable-value").text.strip()
                land = clean_text(prop.find("dt", text="土地面積").find_next("dd").text)
                building = clean_text(prop.find("dt", text="建物面積").find_next("dd").text)
                layout = prop.find("dt", text="間取り").find_next("dd").text.strip()
                age = prop.find("dt", text="築年月").find_next("dd").text.strip()

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
                continue

        page += 1

    df = pd.DataFrame(all_data)
    df = df.dropna(how='all')

    return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
