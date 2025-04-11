from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

app = Flask(__name__)

def clean_text(text):
    return re.sub(r'（.*?）', '', text).strip()

@app.route('/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "URLが指定されていません"}), 400

        # 初期化
        all_properties = []
        page = 1

        while True:
            page_url = url if page == 1 else f"{url}?page={page}"
            res = requests.get(page_url)
            soup = BeautifulSoup(res.content, "html.parser")
            props = soup.find_all(class_=re.compile('^property_unit'))

            if not props:
                break  # 物件がなければ終了

            for prop in props:
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

                    if data_entry not in all_properties:
                        all_properties.append(data_entry)
                except Exception as e:
                    print("データ取得エラー:", e)

            page += 1

        df = pd.DataFrame(all_properties)
        df = df.dropna(how='all')

        return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())

    except Exception as e:
        print("致命的なエラー:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
