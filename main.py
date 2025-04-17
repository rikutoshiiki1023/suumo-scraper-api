from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)

def clean(text):
    return re.sub(r'（.*?）', '', text).strip()

# --------------------
# エリア戸建てパーサー
# --------------------
def parse_area_old_houses(base_url):
    results = [["所在地", "販売価格", "土地面積", "建物面積", "間取り", "築年月"]]
    page = 1

    while True:
        url = f"{base_url}?page={page}" if page > 1 else base_url
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.text, 'html.parser')
        boxes = soup.select('.dottable.dottable--cassette')

        if not boxes:
            break  # 最終ページ

        for box in boxes:
            try:
                location = box.find('dt', string='所在地').find_next('dd').get_text(strip=True)
                price = box.find('dt', string='販売価格').find_next('dd').get_text(strip=True)
                land_area = clean(box.find('dt', string='土地面積').find_next('dd').get_text(strip=True))
                building_area = clean(box.find('dt', string='建物面積').find_next('dd').get_text(strip=True))
                layout = box.find('dt', string='間取り').find_next('dd').get_text(strip=True)
                built_year = box.find('dt', string='築年月').find_next('dd').get_text(strip=True)

                results.append([
                    location, price, land_area, building_area, layout, built_year
                ])
            except Exception as e:
                print(f"Error parsing house on page {page}: {e}")
                continue
        page += 1

    return results

# --------------------
# エリアマンションパーサー
# --------------------
def parse_area_old_apartments(base_url):
    results = [["所在地", "物件名", "販売価格", "専有面積", "バルコニー", "間取り", "築年月"]]
    page = 1

    while True:
        url = f"{base_url}?page={page}" if page > 1 else base_url
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.text, 'html.parser')
        boxes = soup.select('.dottable.dottable--cassette')

        if not boxes:
            break  # 最終ページ

        for box in boxes:
            try:
                location = box.find('dt', string='所在地').find_next('dd').get_text(strip=True)
                name = box.find('dt', string='物件名').find_next('dd').get_text(strip=True)
                price = box.find('dt', string='販売価格').find_next('dd').get_text(strip=True)
                area = clean(box.find('dt', string='専有面積').find_next('dd').get_text(strip=True))
                balcony = box.find('dt', string='バルコニー')
                balcony = clean(balcony.find_next('dd').get_text(strip=True)) if balcony else ''
                layout = box.find('dt', string='間取り').find_next('dd').get_text(strip=True)
                built_year = box.find('dt', string='築年月').find_next('dd').get_text(strip=True)

                results.append([
                    location, name, price, area, balcony, layout, built_year
                ])
            except Exception as e:
                print(f"Error parsing apartment on page {page}: {e}")
                continue
        page += 1

    return results

# --------------------
# APIルーティング
# --------------------
@app.route('/process', methods=['POST'])
def process():
    req_data = request.json
    target = req_data.get('target')
    url = req_data.get('url')

    if not url or not target:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        if target == 'area_old_houses':
            result = parse_area_old_houses(url)
        elif target == 'area_old_apartments':
            result = parse_area_old_apartments(url)
        else:
            return jsonify({'error': 'Invalid target specified'}), 400

        return jsonify({'data': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --------------------
# アプリ起動
# --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
