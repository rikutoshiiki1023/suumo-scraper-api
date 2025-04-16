def parse_client_old_apartments(soup):
    data = {}
    name = ""

    try:
        title_h2 = soup.find("h2", class_="listtitleunit-title")
        if title_h2:
            name = title_h2.get_text(strip=True)

        for dl in soup.find_all("dl", class_="tableinnerbox"):
            key = dl.find("dt").text.strip()
            value = dl.find("dd").text.strip()
            data[key] = value

        result = [
            name,
            data.get("販売価格", ""),
            data.get("所在地", ""),
            data.get("沿線・駅", ""),
            data.get("専有面積", ""),
            data.get("間取り", ""),
            data.get("バルコニー", ""),
            data.get("築年月", ""),
        ]
        return [result]
    except Exception as e:
        print("Error parsing client_old_apartments:", e)
        return []
