def parse_area_old_apartments(soup):
    results = []

    listings = soup.find_all("div", class_="dottable dottable--cassette")
    for item in listings:
        try:
            name = item.find("dt", string="物件名").find_next_sibling("dd").text.strip()
            price = item.find("dt", string="販売価格").find_next("span", class_="dottable-value").text.strip()
            address = item.find("dt", string="所在地").find_next_sibling("dd").text.strip()
            station = item.find("dt", string="沿線・駅").find_next_sibling("dd").text.strip()

            specs = item.find_all("div", class_="dottable-line")[3].find_all("dl")
            area = specs[0].find("dd").text.strip()
            layout = specs[1].find("dd").text.strip()

            balcony = item.find("dt", string="バルコニー").find_next_sibling("dd").text.strip()
            year_built = item.find("dt", string="築年月").find_next_sibling("dd").text.strip()

            results.append([name, price, address, station, area, layout, balcony, year_built])
        except Exception as e:
            print("Error parsing area_old_apartments:", e)
            continue

    return results
