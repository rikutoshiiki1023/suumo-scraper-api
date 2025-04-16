from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

app = Flask(__name__)

def clean_text(text):
    return re.sub(r'（.*?）', '', text).strip()

def scrape_houses(url):
    all_data = []
    page = 1

    while True:
        page_url = f"{url}?page={page}" if page > 1 else url
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
                continue

        page += 1

    return all_data

def scrape_apartments(url):
    all_data = []
    page = 1

    while True:
        page_url = f"{url}?page={page}" if page > 1 else url
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
                name = prop.find("dt", class_="dottable-vm", string="物件名").find_next("span", class_="dottable-value").text.strip()
                price = prop.find("dt", class_="dottable-vm", string="販売価格").find_next("span", class_="dottable-vm").text.strip()
                exclusive = clean_text(prop.find("dt", string="専有面積").find_next("dd").text)
                balcony = clean_text(prop.find("dt", string="バルコニー").find_next("dd").text)
                layout = prop.find("dt", string="間取り").find_next("dd").text.strip()
                age = prop.find("dt", string="築年月").find_next("dd").text.strip()

                data_entry = {
                    "所在地": location,
                    "物件名": name,
                    "販売価格": price,
                    "専有面積": exclusive,
                    "バルコニー": balcony,
                    "間取り": layout,
                    "築年月": age
                }
                all_data.append(data_entry)
            except AttributeError:
                continue

        page += 1

    return all_data

# ① area_old_houses（戸建て・パス）
@app.route('/scrape_old_houses_from_path', methods=['POST'])
def scrape_old_houses_from_path():
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "パスが指定されていません"}), 400
    base_url = f"https://suumo.jp/chukoikkodate/{path}"
    result = scrape_houses(base_url)
    if not result:
        return jsonify({"error": "物件データが見つかりませんでした"}), 404
    df = pd.DataFrame(result)
    return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())

# ② area_old_apartments（マンション・パス）
@app.route('/scrape_old_apartments_from_path', methods=['POST'])
def scrape_old_apartments_from_path():
    data = request.get_json()
    path = data.get("path")
    if not path:
        return jsonify({"error": "パスが指定されていません"}), 400
    base_url = f"https://suumo.jp/chuko/{path}"
    result = scrape_apartments(base_url)
    if not result:
        return jsonify({"error": "物件データが見つかりませんでした"}), 404
    df = pd.DataFrame(result)
    return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())

# ③ client_old_houses（戸建て・URL）
@app.route('/scrape_old_houses_from_url', methods=['POST'])
def scrape_old_houses_from_url():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "URLが指定されていません"}), 400
    result = scrape_houses(url)
    if not result:
        return jsonify({"error": "物件データが見つかりませんでした"}), 404
    df = pd.DataFrame(result)
    return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())

# ④ client_old_apartments（マンション・URL）
@app.route('/scrape_old_apartments_from_url', methods=['POST'])
def scrape_old_apartments_from_url():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "URLが指定されていません"}), 400
    result = scrape_apartments(url)
    if not result:
        return jsonify({"error": "物件データが見つかりませんでした"}), 404
    df = pd.DataFrame(result)
    return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
