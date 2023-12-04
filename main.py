from typing import Dict
from car_data_fetcher import CarDataFetcher
from config import headers, cookies

def main():
    base_url = 'https://api.encar.com/search/car/list/premium'
    manufacturer = "기아"
    category = "경차"
    year_from = "202000"
    year_to = "202399"
    page_count = 30

    car_data_fetcher = CarDataFetcher(base_url, manufacturer, category, year_from, year_to, page_count, headers, cookies)
    car_data_fetcher.fetch_and_save_data('car_details.json', 'car_details.md')

if __name__ == "__main__":
    main()
