from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

app = Flask(__name__)

def clean_text(text):
    return re.sub(r'（.*?）', '', text).strip() if text else ""

def get_next_text(prop, dt_text):
    dt_tag = prop.find("dt", text=dt_text)
    if dt_tag:
        dd_tag = dt_tag.find_next("dd")
        if dd_tag:
            return dd_tag.text.strip()
    return ""

def get_next_value(prop, dt_text):
    dt_tag = prop.find("dt", class_="dottable-vm", text=dt_text)
    if dt_tag:
        value_tag = dt_tag.find_next("span", class_="dottable-value")
        if value_tag:
            return value_tag.text.strip()
    return ""

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URLが指定されていません"}), 400

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        property_data = []

        for prop in soup.find_all(class_=re.compile('^property_unit')):
            location = get_next_text(prop, "所在地")
            price = get_next_value(prop, "販売価格")
            land = clean_text(get_next_text(prop, "土地面積"))
            building = clean_text(get_next_text(prop, "建物面積"))
            layout = get_next_text(prop, "間取り")
            age = get_next_text(prop, "築年月")

            data_entry = {
                "所在地": location,
                "販売価格": price,
                "土地面積": land,
                "建物面積": building,
                "間取り": layout,
                "築年月": age
            }

            if any(data_entry.values()) and data_entry not in property_data:
                property_data.append(data_entry)

        df = pd.DataFrame(property_data)
        return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
