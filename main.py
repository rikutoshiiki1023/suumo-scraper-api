from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)

def clean_text(text):
    return re.sub(r'（.*?）', '', text).strip() if text else ""

# ---------- パーサー定義 ----------

def parse_area_old_houses(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "販売価格", "土地面積", "建物面積", "間取り", "築年月"]]
    boxes = soup.select('.dottable.dottable--cassette')

    for box in boxes:
        try:
            location = box.find('dt', string='所在地').find_next('dd').text.strip()
            price = box.find('dt', string='販売価格').find_next('dd').text.strip()
            land_area = clean_text(box.find('dt', string='土地面積').find_next('dd').text.strip())
            building_area = clean_text(box.find('dt', string='建物面積').find_next('dd').text.strip())
            layout = box.find('dt', string='間取り').find_next('dd').text.strip()
            built_year = box.find('dt', string='築年月').find_next('dd').text.strip()
            results.append([location, price, land_area, building_area, layout, built_year])
        except Exception as e:
            print(f"[area_old_houses] Error: {e}")
            continue

    return results

def parse_area_old_apartments(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "物件名", "販売価格", "専有面積", "バルコニー", "間取り", "築年月"]]
    boxes = soup.select('.dottable.dottable--cassette')

    for box in boxes:
        try:
            location = box.find('dt', string='所在地').find_next('dd').text.strip()
            name = box.find('dt', string='物件名').find_next('dd').text.strip()
            price = box.find('dt', string='販売価格').find_next('dd').text.strip()
            area = clean_text(box.find('dt', string='専有面積').find_next('dd').text.strip())
            balcony = clean_text(box.find('dt', string='バルコニー').find_next('dd').text.strip())
            layout = box.find('dt', string='間取り').find_next('dd').text.strip()
            built_year = box.find('dt', string='築年月').find_next('dd').text.strip()
            results.append([location, name, price, area, balcony, layout, built_year])
        except Exception as e:
            print(f"[area_old_apartments] Error: {e}")
            continue

    return results

def parse_client_old_houses(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "販売価格", "土地面積", "建物面積", "間取り", "築年月"]]
    boxes = soup.select("li.cassette.js-bukkenCassette")

    for box in boxes:
        try:
            dl_elements = box.select("dl.tableinnerbox")
            data = {}
            for dl in dl_elements:
                key = dl.find("dt").text.strip()
                value = dl.find("dd").text.strip()
                data[key] = value

            location = data.get("所在地", "")
            price = data.get("販売価格", "")
            land_area = clean_text(data.get("土地面積", ""))
            building_area = clean_text(data.get("建物面積", ""))
            layout = data.get("間取り", "")
            built_year = data.get("築年月", "")
            results.append([location, price, land_area, building_area, layout, built_year])
        except Exception as e:
            print(f"[client_old_houses] Error: {e}")
            continue

    return results

def parse_client_old_apartments(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "物件名", "販売価格", "専有面積", "バルコニー", "間取り", "築年月"]]
    boxes = soup.select("li.cassette.js-bukkenCassette")

    for box in boxes:
        try:
            name = box.select_one(".listtitleunit-title a").text.strip()
            dl_elements = box.select("dl.tableinnerbox")
            data = {}
            for dl in dl_elements:
                key = dl.find("dt").text.strip()
                value = dl.find("dd").text.strip()
                data[key] = value

            location = data.get("所在地", "")
            price = data.get("販売価格", "")
            area = clean_text(data.get("専有面積", ""))
            balcony = clean_text(data.get("バルコニー", ""))
            layout = data.get("間取り", "")
            built_year = data.get("築年月", "")
            results.append([location, name, price, area, balcony, layout, built_year])
        except Exception as e:
            print(f"[client_old_apartments] Error: {e}")
            continue

    return results

# ---------- APIエンドポイント ----------

@app.route('/process', methods=['POST'])
def process():
    req_data = request.json
    target = req_data.get('target')
    url = req_data.get('url')

    if not url or not target:
        return jsonify({'error': 'Missing required parameters'}), 400

    result = []
    page = 1

    while True:
        paged_url = f"{url}?page={page}" if page > 1 else url
        try:
            res = requests.get(paged_url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200:
                break
            html = res.text

            if target == 'area_old_houses':
                parsed = parse_area_old_houses(html)
            elif target == 'area_old_apartments':
                parsed = parse_area_old_apartments(html)
            elif target == 'client_old_houses':
                parsed = parse_client_old_houses(html)
            elif target == 'client_old_apartments':
                parsed = parse_client_old_apartments(html)
            else:
                return jsonify({'error': 'Invalid target'}), 400

            if len(parsed) <= 1:
                break  # データが空 or ヘッダーのみ
            if page == 1:
                result.extend(parsed)
            else:
                result.extend(parsed[1:])  # 2ページ目以降はヘッダー除く

            page += 1

        except Exception as e:
            print(f"[ERROR] Failed on page {page}: {e}")
            break

    return jsonify({'data': result})

# ---------- Flask起動 ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
