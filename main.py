@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    path = data.get("url")  # パスだけが渡ってくる（例: nagano/sc_20206/）

    if not path:
        return jsonify({"error": "URLパスが指定されていません"}), 400

    base_url = f"https://suumo.jp/chukoikkodate/{path.strip('/')}/"
    property_data = []

    page = 1
    while True:
        url = base_url if page == 1 else f"{base_url}?page={page}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        units = soup.find_all(class_=re.compile('^property_unit'))
        if not units:
            break  # 次のページがなければ終了

        for prop in units:
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
        page += 1

    df = pd.DataFrame(property_data)
    df = df.dropna(how='all')

    return jsonify([df.columns.tolist()] + df.fillna("").values.tolist())
