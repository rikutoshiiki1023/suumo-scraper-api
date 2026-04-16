from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import os
import time

app = Flask(__name__)
CORS(app)

# 都道府県名 → SUUMOパスコードマッピング
PREFECTURE_MAP = {
    "北海道": "hokkaido_",
    "青森県": "aomori",
    "岩手県": "iwate",
    "宮城県": "miyagi",
    "秋田県": "akita",
    "山形県": "yamagata",
    "福島県": "fukushima",
    "茨城県": "ibaraki",
    "栃木県": "tochigi",
    "群馬県": "gunma",
    "埼玉県": "saitama",
    "千葉県": "chiba",
    "東京都": "tokyo",
    "神奈川県": "kanagawa",
    "新潟県": "niigata",
    "富山県": "toyama",
    "石川県": "ishikawa",
    "福井県": "fukui",
    "山梨県": "yamanashi",
    "長野県": "nagano",
    "岐阜県": "gifu",
    "静岡県": "shizuoka",
    "愛知県": "aichi",
    "三重県": "mie",
    "滋賀県": "shiga",
    "京都府": "kyoto",
    "大阪府": "osaka",
    "兵庫県": "hyogo",
    "奈良県": "nara",
    "和歌山県": "wakayama",
    "鳥取県": "tottori",
    "島根県": "shimane",
    "岡山県": "okayama",
    "広島県": "hiroshima",
    "山口県": "yamaguchi",
    "徳島県": "tokushima",
    "香川県": "kagawa",
    "愛媛県": "ehime",
    "高知県": "kochi",
    "福岡県": "fukuoka",
    "佐賀県": "saga",
    "長崎県": "nagasaki",
    "熊本県": "kumamoto",
    "大分県": "oita",
    "宮崎県": "miyazaki",
    "鹿児島県": "kagoshima",
    "沖縄県": "okinawa",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def clean_text(text):
    return re.sub(r'（.*?）', '', text).strip() if text else ""


def parse_price(price_str):
    """価格文字列を万円の整数に変換 (例: "2,500万円" → 2500)"""
    try:
        s = (price_str
             .replace(',', '')
             .replace('円', '')
             .replace(' ', '')
             .replace('\u00a0', ''))
        if '億' in s:
            parts = s.split('億')
            oku = int(parts[0]) * 10000
            man_str = parts[1].replace('万', '').strip() if parts[1] else '0'
            man = int(man_str) if man_str else 0
            return oku + man
        elif '万' in s:
            return int(s.replace('万', '').strip())
        return None
    except Exception:
        return None


def categorize_price(price_man):
    if price_man is None:
        return None
    if price_man <= 1500:
        return "0-1500万"
    elif price_man <= 3000:
        return "1501-3000万"
    else:
        return "3001万-"


def compute_segments(data, price_col_index):
    """スクレイピングデータを価格セグメントに分類して件数を返す"""
    segments = {"0-1500万": 0, "1501-3000万": 0, "3001万-": 0}
    if len(data) <= 1:
        return segments
    for row in data[1:]:  # ヘッダー行をスキップ
        if len(row) > price_col_index:
            price = parse_price(row[price_col_index])
            cat = categorize_price(price)
            if cat:
                segments[cat] += 1
    return segments


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


def scrape_all_pages(url, target):
    """指定URLのすべてのページをスクレイピングして結果を返す"""
    result = []
    page = 1
    while True:
        paged_url = f"{url}?page={page}" if page > 1 else url
        try:
            res = requests.get(paged_url, headers=HEADERS, timeout=20)
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
                break

            if len(parsed) <= 1:
                break
            if page == 1:
                result.extend(parsed)
            else:
                result.extend(parsed[1:])  # 2ページ目以降はヘッダー除く
            page += 1
            time.sleep(0.5)  # レート制限対策
        except Exception as e:
            print(f"[ERROR] Failed on page {page}: {e}")
            break
    return result


# ---------- APIエンドポイント ----------

@app.route('/process', methods=['POST'])
def process():
    """既存エンドポイント（後方互換性のため維持）"""
    req_data = request.json
    target = req_data.get('target')
    url = req_data.get('url')
    if not url or not target:
        return jsonify({'error': 'Missing required parameters'}), 400
    result = scrape_all_pages(url, target)
    return jsonify({'data': result})


@app.route('/search-area', methods=['POST'])
def search_area():
    """
    日本語のエリア名からSUUMOのエリアパスを検索して返す。
    入力例: { "area_name": "兵庫県姫路市" }
    出力例: { "path": "hyogo/sc_himeji", "city_name": "姫路市" }
    """
    req_data = request.get_json()
    area_name = req_data.get('area_name', '').strip()

    if not area_name:
        return jsonify({'error': 'area_name is required'}), 400

    # 都道府県コードを特定
    pref_code = None
    city_query = area_name

    for pref_name, code in PREFECTURE_MAP.items():
        if area_name.startswith(pref_name) or pref_name in area_name:
            pref_code = code
            city_query = area_name.replace(pref_name, '').strip()
            break

    if not pref_code:
        return jsonify({
            'error': '都道府県名を先頭に含めてください（例：兵庫県姫路市）'
        }), 400

    if not city_query:
        return jsonify({
            'error': '市区町村名を含めてください（例：兵庫県姫路市）'
        }), 400

    # SUUMO都道府県ページをスクレイピングして市区町村リンクを探す
    pref_url = f"https://suumo.jp/chukomansion/{pref_code}/"

    try:
        res = requests.get(pref_url, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            return jsonify({
                'error': f'SUUMO接続エラー (status: {res.status_code})'
            }), 500

        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=True)

        city_query_base = city_query.rstrip('市区町村郡')
        area_link_pattern = re.compile(
            rf'^/chukomansion/{re.escape(pref_code)}/[a-z_]+/$'
        )
        best_match = None

        for link in links:
            href = link.get('href', '')
            text = link.text.strip()

            if not area_link_pattern.search(href):
                continue

            text_base = text.rstrip('市区町村郡')

            # 完全一致なら即時返却
            if text == city_query or text == city_query + '市' or text == city_query + '区':
                parts = href.strip('/').split('/')
                if len(parts) >= 3:
                    return jsonify({
                        'path': f"{parts[1]}/{parts[2]}",
                        'city_name': text
                    })

            # 部分一致を候補として保持
            if (city_query in text or text_base in city_query_base
                    or city_query_base in text_base):
                parts = href.strip('/').split('/')
                if len(parts) >= 3 and best_match is None:
                    best_match = {
                        'path': f"{parts[1]}/{parts[2]}",
                        'city_name': text
                    }

        if best_match:
            return jsonify(best_match)

        return jsonify({
            'error': (
                f'"{city_query}" はSUUMOで見つかりませんでした。'
                '都道府県名付きで再入力してください（例：兵庫県姫路市）'
            )
        }), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    エリアパス・企業URLを受け取り、エリア全体と企業のシェアを計算して返す。
    入力例:
      {
        "area_path": "hyogo/sc_himeji",
        "condo_url": "https://suumo.jp/chukomansion/__JJ_...",
        "house_url": "https://suumo.jp/chukoikkodate/__JJ_..."
      }
    """
    req_data = request.get_json()
    area_path = req_data.get('area_path', '').strip()
    condo_url = req_data.get('condo_url', '').strip()
    house_url = req_data.get('house_url', '').strip()

    if not area_path:
        return jsonify({'error': 'area_path is required'}), 400

    # ── マンション分析 ──
    # area_old_apartments ヘッダー: 所在地(0), 物件名(1), 販売価格(2), ...
    area_condo_data = scrape_all_pages(
        f"https://suumo.jp/chukomansion/{area_path}/", 'area_old_apartments'
    )
    area_condo_count = max(0, len(area_condo_data) - 1)

    client_condo_data = []
    if condo_url:
        client_condo_data = scrape_all_pages(condo_url, 'client_old_apartments')
    client_condo_count = max(0, len(client_condo_data) - 1)

    condo_share = (
        round(client_condo_count / area_condo_count * 100, 2)
        if area_condo_count > 0 else 0.0
    )

    area_condo_seg = compute_segments(area_condo_data, 2)
    client_condo_seg = compute_segments(client_condo_data, 2)

    condo_segments = {}
    for seg in ["0-1500万", "1501-3000万", "3001万-"]:
        a = area_condo_seg.get(seg, 0)
        c = client_condo_seg.get(seg, 0)
        condo_segments[seg] = {
            "area": a,
            "client": c,
            "share": round(c / a * 100, 2) if a > 0 else 0.0
        }

    # ── 戸建て分析 ──
    # area_old_houses ヘッダー: 所在地(0), 販売価格(1), ...
    area_house_data = scrape_all_pages(
        f"https://suumo.jp/chukoikkodate/{area_path}/", 'area_old_houses'
    )
    area_house_count = max(0, len(area_house_data) - 1)

    client_house_data = []
    if house_url:
        client_house_data = scrape_all_pages(house_url, 'client_old_houses')
    client_house_count = max(0, len(client_house_data) - 1)

    house_share = (
        round(client_house_count / area_house_count * 100, 2)
        if area_house_count > 0 else 0.0
    )

    area_house_seg = compute_segments(area_house_data, 1)
    client_house_seg = compute_segments(client_house_data, 1)

    house_segments = {}
    for seg in ["0-1500万", "1501-3000万", "3001万-"]:
        a = area_house_seg.get(seg, 0)
        c = client_house_seg.get(seg, 0)
        house_segments[seg] = {
            "area": a,
            "client": c,
            "share": round(c / a * 100, 2) if a > 0 else 0.0
        }

    return jsonify({
        'area_path': area_path,
        'condo': {
            'area_total': area_condo_count,
            'client_total': client_condo_count,
            'share': condo_share,
            'segments': condo_segments
        },
        'house': {
            'area_total': area_house_count,
            'client_total': client_house_count,
            'share': house_share,
            'segments': house_segments
        }
    })


# ---------- Flask起動 ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
