def parse_area_old_apartments(soup):
    results = []

    listings = soup.find_all("div", class_="dottable dottable--cassette")
    for item in listings:
        try:
            address = item.find("dt", string="所在地").find_next_sibling("dd").text.strip()
            name = item.find("dt", string="物件名").find_next_sibling("dd").text.strip()
            price = item.find("dt", string="販売価格").find_next("span", class_="dottable-value").text.strip()
            area = item.find("dt", string="専有面積").find_next_sibling("dd").text.strip()
            balcony = item.find("dt", string="バルコニー").find_next_sibling("dd").text.strip()
            layout = item.find("dt", string="間取り").find_next_sibling("dd").text.strip()
            year_built = item.find("dt", string="築年月").find_next_sibling("dd").text.strip()

            results.append([address, name, price, area, balcony, layout, year_built])
        except Exception as e:
            print("Error parsing area_old_apartments:", e)
            continue

    return results
