import requests
from bs4 import BeautifulSoup


def parse_area_old_houses(path: str):
    """
    SUUMOのエリア別 中古戸建て情報をスクレイピングする関数。
    path（例: 'ikkodate/tokyo/SC13103/'）を元に複数ページを巡回し、
    タイトル・価格・住所・土地面積・建物面積を取得する。

    Returns:
        List[List[str]]: 2次元リスト。1行が1物件。
    """
    results = []
    page = 1

    while True:
        url = f"https://suumo.jp/chuko{path}?page={page}"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        # 物件情報の親要素を取得
        items = soup.select(".cassetteitem")

        # ページ内に物件がない＝最終ページ
        if not items:
            break

        for item in items:
            try:
                title = item.select_one(".cassetteitem_content-title").text.strip()
                price = item.select_one(".cassetteitem_price--price").text.strip()
                address = item.select_one(".cassetteitem_detail-col1").text.strip()
                land_area = item.select_one(".cassetteitem_detail-col3").text.strip()
                building_area = item.select_one(".cassetteitem_detail-col4").text.strip()

                results.append([
                    address, title, price, land_area, building_area
                ])
            except Exception as e:
                # 不正な構造の物件があればスキップ
                print(f"Error parsing item on page {page}: {e}")
                continue

        page += 1

    return results
