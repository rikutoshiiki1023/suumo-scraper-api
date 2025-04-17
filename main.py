from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# ========== 戸建てパーサー ==========
def parse_old_houses(html):
    soup = BeautifulSoup(html, 'html.parser')
    data_list = []

    property_boxes = soup.select('.cassettebox')
    for box in property_boxes:
        try:
            name = box.select_one('.listtitleunit-title a').get_text(strip=True)
            price = box.find('dt', string='価格').find_next('dd').get_text(strip=True)
            location = box.find('dt', string='所在地').find_next('dd').get_text(strip=True)
            land_area = box.find('dt', string='土地面積').find_next('dd').get_text(strip=True)
            building_area = box.find('dt', string='建物面積').find_next('dd').get_text(strip=True)
            layout = box.find('dt', string='間取り').find_next('dd').get_text(strip=True)
            built_year = box.find('dt', string='築年月').find_next('dd').get_text(strip=True)

            data_list.append([
                location,
                name,
                price,
                land_area,
                building_area,
                layout,
                built_year
            ])
        except Exception as e:
            print(f"Error parsing house: {e}")
            continue

    return data_list

# ========== マンションパーサー ==========
def parse_old_apartments(html):
    soup = BeautifulSoup(html, 'html.parser')
    data_list = []

    property_boxes = soup.select('.cassettebox')
    for box in property_boxes:
        try:
            name = box.select_one('.listtitleunit-title a').get_text(strip=True)
            price = box.find('dt', string='販売価格').find_next('dd').get_text(strip=True)
            location = box.find('dt', string='所在地').find_next('dd').get_text(strip=True)
            area = box.find('dt', string='専有面積').find_next('dd').get_text(strip=True)
            balcony = box.find('dt', string='バルコニー')
            balcony = balcony.find_next('dd').get_text(strip=True) if balcony else ''
            layout = box.find('dt', string='間取り').find_next('dd').get_text(strip=True)
            built_year = box.find('dt', string='築年月').find_next('dd').get_text(strip=True)

            data_list.append([
                location,
                name,
                price,
                area,
                balcony,
                layout,
                built_year
            ])
        except Exception as e:
            print(f"Error parsing apartment: {e}")
            continue

    return data_list

# ========== APIエンドポイント（ページネーション対応） ==========
@app.route('/process', methods=['POST'])
def process():
    req_data = request.json
    target = req_data.get('target')
    base_url = req_data.get('url')

    if not base_url or not target:
        return jsonify({'error': 'Missing required parameters'}), 400

    all_data = []
    page = 1

    while True:
        url = base_url
        if page > 1:
            if "?" in base_url:
                url += f"&page={page}"
            else:
                url += f"?page={page}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            html = response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

        # パース処理
        if target in ['area_old_houses', 'client_old_houses']:
            parsed = parse_old_houses(html)
        elif target in ['area_old_apartments', 'client_old_apartments']:
            parsed = parse_old_apartments(html)
        else:
            return jsonify({'error': 'Invalid target specified'}), 400

        if not parsed:
            break  # 次ページにデータがない＝終了

        all_data.extend(parsed)
        page += 1

    return jsonify({'data': all_data})

# ========== Flaskアプリ起動 ==========
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000, debug=True)
