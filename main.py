from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    req_data = request.json
    target = req_data.get('target')
    url = req_data.get('url')

    if not url or not target:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        html = response.text
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching page: {str(e)}'}), 400

    if target == 'area_old_houses':
        result = parse_old_houses(html)
    else:
        return jsonify({'error': 'Invalid target specified'}), 400

    return jsonify({'data': result})

def parse_old_houses(html):
    soup = BeautifulSoup(html, 'html.parser')
    data_list = []

    property_boxes = soup.select('.property_unit-body')
    for box in property_boxes:
        try:
            location = box.find('dt', string='所在地').find_next('dd').get_text(strip=True)
            price = box.find('dt', string='販売価格').find_next('dd').find('span', class_='dottable-value').get_text(strip=True)
            land_area = box.find('dt', string='土地面積').find_next('dd').get_text(strip=True)
            building_area = box.find('dt', string='建物面積').find_next('dd').get_text(strip=True)
            layout = box.find('dt', string='間取り').find_next('dd').get_text(strip=True)
            built_year = box.find('dt', string='築年月').find_next('dd').get_text(strip=True)

            data_list.append([
                location,
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

if __name__ == '__main__':
    app.run(debug=True)
