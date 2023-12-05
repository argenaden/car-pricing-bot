import requests
import json
from typing import Dict
import argparse

class CarDataFetcher:
    def __init__(self, base_url, manufacturer, category, year_from, year_to, page_count, headers, cookies):
        self.base_url = base_url
        self.manufacturer = manufacturer
        self.category = category
        self.year_from = year_from
        self.year_to = year_to
        self.page_count = page_count
        self.headers = headers
        self.cookies = cookies

    def fetch_car_data(self, page):
        params = self.create_query_format(page)
        url = f"{self.base_url}?count=true&q={params['q']}&sr={params['sr']}"

        try:
            response = requests.get(url, headers=self.headers, cookies=self.cookies)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        except requests.exceptions.RequestException as e:
            print(f"Request failed with exception: {e}")
            return None

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

    def create_query_format(self, page) -> Dict[str, str]:
        params = {
            "count": "true",
            "q": f"(And.Hidden.N._.Category.{self.category}._.(C.CarType.Y._.(C.Manufacturer.{self.manufacturer}._.ModelGroup.%EB%A0%88%EC%9D%B4.))_.Year.range({self.year_from}..{self.year_to}).)",
            "sr": f"|PriceAsc|{(page * 10) * 2}|20"
        }
        return params

    def save_to_json(self, data, filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_json(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)

    def create_markdown_table(self, data, md_filename):
        if not data:
            print("No data to create a table.")
            return
        
        # convert dict to list
        data = list(data.values())

        headers = data[0].keys()
        md_table = "| " + " | ".join(headers) + " |\n"  # Table header
        md_table += "| " + " | ".join(["-" * len(h) for h in headers]) + " |\n"  # Separator

        for entry in data:
            row = "| " + " | ".join(str(entry.get(h, '')) for h in headers) + " |"
            md_table += row + "\n"

        with open(md_filename, 'w', encoding='utf-8') as file:
            file.write(md_table)

    def fetch_and_save_data(self, output_json_filename, output_md_filename):
        all_car_data = {}

        for page in range(self.page_count):
            raw_data = self.fetch_car_data(page)
            if raw_data is None:
                break

            car_data = raw_data.get('SearchResults', [])
            if not car_data:
                print(f"No data found for page {page}.")
                continue

            for car in car_data:
                id = car.get('Id', '')
                all_car_data[id] = {
                    'Manufacturer': car.get('Manufacturer', ''),
                    'Price': car.get('Price', ''),
                    'Model': car.get('Model', ''),
                    'Badge': car.get('Badge', ''),
                    'BadgeDetail': car.get('BadgeDetail', ''),
                    'GreenType': car.get('GreenType', ''),
                    'FuelType': car.get('FuelType', ''),
                    'Year': car.get('Year', ''),
                    'Mileage': car.get('Mileage', ''),
                    'ServiceCopyCar': car.get('ServiceCopyCar', ''),
                    'OfficeCityState': car.get('OfficeCityState', '')
                }

        if all_car_data:
            self.save_to_json(all_car_data, output_json_filename)
            self.create_markdown_table(all_car_data, output_md_filename)
        else:
            print("No data fetched or all data was empty.")