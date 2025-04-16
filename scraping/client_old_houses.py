def parse_client_old_houses(soup):
    data = {}

    try:
        for dl in soup.find_all("dl", class_="tableinnerbox"):
            key = dl.find("dt").text.strip()
            value = dl.find("dd").text.strip()
            data[key] = value

        result = [
            data.get("物件名", ""),  # 物件名を取得
            data.get("販売価格", ""),
            data.get("所在地", ""),
            data.get("土地面積", ""),
            data.get("建物面積", ""),
            data.get("間取り", ""),
            data.get("築年月", ""),
        ]
        return [result]
    except Exception as e:
        print("Error parsing client_old_houses:", e)
        return []
