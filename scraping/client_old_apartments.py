from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def parse_client_old_apartments(html):
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
            print(f"Error parsing one property: {e}")
            continue

    return data_list

@app.route('/process', methods=['POST'])
def process():
    req_data = request.json
    target = req_data.get('target')
    url = req_data.get('url')

    try:
        response = requests.get(url)
        response.raise_for_status()  # ここでリクエストエラーをキャッチ
        response.encoding = response.apparent_encoding
        html = response.text
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching page: {str(e)}'}), 400

    if target == 'client_old_apartments':
        result = parse_apartment(html)
        return jsonify({'data': result})

    return jsonify({'error': 'Invalid target specified'}), 400

if __name__ == "__main__":
    app.run(debug=True)
