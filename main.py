from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

app = Flask(__name__)

def clean_text(text):
    """不要な文字列を削除するクリーニング関数"""
    return re.sub(r'（.*?）', '', text).strip()

@app.route('/process', methods=['POST'])
def process():
    # スクレイピング処理
    url = "https://suumo.jp/jj/bukken/ichiran/JJ012FC001/?ar=020&bs=021&sc=02201&ta=02&po=0&pj=1&pc=100"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    property_data = []

    for prop in soup.find_all(class_=re.compile('^property_unit')): 
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

            if data_entry not in property_data:
                property_data.append(data_entry)
        except AttributeError:
            pass

    df = pd.DataFrame(property_data)
    df = df.dropna(how='all')

    # GASに渡す形：JSON配列に変換
    return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())

if __name__ == "__main__":
    app.run(port=5000)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Renderが指定したポート番号を使う
    app.run(host="0.0.0.0", port=port)        # 必ず 0.0.0.0 にバインド！
