from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)

# 共通：カッコ内の情報を削除する関数
def clean_area(text):
    return re.sub(r'（.*?）', '', text).strip()

# ------------------------
# area_old_houses パーサー
# ------------------------
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

# ----------------------------
# area_old_apartments パーサー
# ----------------------------
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

# ----------------------------
# client_old_houses パーサー
# ----------------------------
def parse_client_old_houses(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "販売価格", "土地面積", "建物面積", "間取り", "築年月"]]
    boxes = soup.select("li.cassette.js-bukkenCassette")

    for box in boxes:
        try:
            details = {
                dl.find("dt").get_text(strip=True): dl.find("dd").get_text(strip=True)
                for dl in box.select("dl.tableinnerbox")
            }

            location = details.get("所在地", "")
            price = details.get("販売価格", "")
            land_area = clean_area(details.get("土地面積", ""))
            building_area = clean_area(details.get("建物面積", ""))
            layout = details.get("間取り", "")
            built_year = details.get("築年月", "")

            results.append([location, price, land_area, building_area, layout, built_year])
        except Exception as e:
            print(f"Error parsing client_old_houses: {e}")
            continue

    return results

# ---------------------------------
# client_old_apartments パーサー
# ---------------------------------
def parse_client_old_apartments(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = [["所在地", "物件名", "販売価格", "専有面積", "バルコニー", "間取り", "築年月"]]
    boxes = soup.select("li.cassette.js-bukkenCassette")

    for box in boxes:
        try:
            details = {
                dl.find("dt").get_text(strip=True): dl.find("dd").get_text(strip=True)
                for dl in box.select("dl.tableinnerbox")
            }

            name = box.select_one('.listtitleunit-title a')
            name = name.get_text(strip=True) if name else ""

            location = details.get("所在地", "")
            price = details.get("販売価格", "")
            area = clean_area(details.get("専有面積", ""))
            balcony = clean_area(details.get("バルコニー", ""))
            layout = details.get("間取り", "")
            built_year = details.get("築年月", "")

            results.append([location, name, price, area, balcony, layout, built_year])
        except Exception as e:
            print(f"Error parsing client_old_apartments: {e}")
            continue

    return results

# ----------------------
# APIの共通処理
# ----------------------
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
            elif target == 'client_old_houses':
                parsed = parse_client_old_houses(html)
            elif target == 'client_old_apartments':
                parsed = parse_client_old_apartments(html)
            else:
                return jsonify({'error': 'Invalid target specified'}), 400

            if len(parsed) <= 1:
                break  # ヘッダーのみなら終了

            if page == 1:
                result.extend(parsed)
            else:
                result.extend(parsed[1:])  # 2ページ目以降はヘッダー除外

            page += 1

        return jsonify({'data': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------------
# Flaskアプリ起動
# ----------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
