from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)

def clean_area(text):
    return re.sub(r'（.*?）', '', text).strip()

# --------------------- エリア戸建て ---------------------
def parse_area_old_houses(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "販売価格", "土地面積", "建物面積", "間取り", "築年月"]]
    boxes = soup.select('.dottable.dottable--cassette')

    for box in boxes:
        try:
            location = box.find('dt', string='所在地').find_next('dd').get_text(strip=True)
            price = box.find('dt', string='販売価格').find_next('dd').get_text(strip=True)
            land_area = clean_area(box.find('dt', string='土地面積').find_next('dd').get_text(strip=True))
            building_area = clean_area(box.find('dt', string='建物面積').find_next('dd').get_text(strip=True))
            layout = box.find('dt', string='間取り').find_next('dd').get_text(strip=True)
            built_year = box.find('dt', string='築年月').find_next('dd').get_text(strip=True)
            results.append([location, price, land_area, building_area, layout, built_year])
        except Exception as e:
            print(f"Error parsing area_old_house: {e}")
            continue

    return results

# --------------------- エリアマンション ---------------------
def parse_area_old_apartments(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "物件名", "販売価格", "専有面積", "バルコニー", "間取り", "築年月"]]
    boxes = soup.select('.dottable.dottable--cassette')

    for box in boxes:
        try:
            location = box.find('dt', string='所在地').find_next('dd').get_text(strip=True)
            name = box.find('dt', string='物件名').find_next('dd').get_text(strip=True)
            price = box.find('dt', string='販売価格').find_next('dd').get_text(strip=True)
            area = clean_area(box.find('dt', string='専有面積').find_next('dd').get_text(strip=True))
            balcony = clean_area(box.find('dt', string='バルコニー').find_next('dd').get_text(strip=True))
            layout = box.find('dt', string='間取り').find_next('dd').get_text(strip=True)
            built_year = box.find('dt', string='築年月').find_next('dd').get_text(strip=True)
            results.append([location, name, price, area, balcony, layout, built_year])
        except Exception as e:
            print(f"Error parsing area_old_apartment: {e}")
            continue

    return results

# --------------------- クライアントマンション ---------------------
def parse_client_old_apartments(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "物件名", "販売価格", "専有面積", "バルコニー", "間取り", "築年月"]]
    boxes = soup.select("li.cassette.js-bukkenCassette")

    for box in boxes:
        try:
            name = box.select_one('.listtitleunit-title a').get_text(strip=True)
            data = {}
            for dl in box.select('dl.tableinnerbox'):
                key = dl.find('dt').get_text(strip=True)
                value = dl.find('dd').get_text(strip=True)
                data[key] = value

            results.append([
                data.get("所在地", ""),
                name,
                data.get("販売価格", ""),
                clean_area(data.get("専有面積", "")),
                clean_area(data.get("バルコニー", "")),
                data.get("間取り", ""),
                data.get("築年月", "")
            ])
        except Exception as e:
            print(f"Error parsing client_old_apartment: {e}")
            continue

    return results

# --------------------- クライアント戸建て ---------------------
def parse_client_old_houses(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "販売価格", "土地面積", "建物面積", "間取り", "築年月"]]
    boxes = soup.select("li.cassette.js-bukkenCassette")

    for box in boxes:
        try:
            data = {}
            for dl in box.select('dl.tableinnerbox'):
                key = dl.find('dt').get_text(strip=True)
                value = dl.find('dd').get_text(strip=True)
                data[key] = value

            results.append([
                data.get("所在地", ""),
                data.get("販売価格", ""),
                clean_area(data.get("土地面積", "")),
                clean_area(data.get("建物面積", "")),
                data.get("間取り", ""),
                data.get("築年月", "")
            ])
        except Exception as e:
            print(f"Error parsing client_old_house: {e}")
            continue

    return results

# --------------------- APIルーティング ---------------------
@app.route('/process', methods=['POST'])
def process():
    req_data = request.json
    target = req_data.get('target')
    url = req_data.get('url')

    if not url or not target:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        result = []
        page = 1
        while True:
            paged_url = f"{url}?page={page}" if page > 1 else url
            res = requests.get(paged_url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200:
                break
            html = res.text

            if target == 'area_old_houses':
                parsed = parse_area_old_houses(html)
            elif target == 'area_old_apartments':
                parsed = parse_area_old_apartments(html)
            elif target == 'client_old_apartments':
                parsed = parse_client_old_apartments(html)
            elif target == 'client_old_houses':
                parsed = parse_client_old_houses(html)
            else:
                return jsonify({'error': 'Invalid target specified'}), 400

            if len(parsed) <= 1:
                break
            if page == 1:
                result.extend(parsed)
            else:
                result.extend(parsed[1:])
            page += 1

        return jsonify({'data': result})
