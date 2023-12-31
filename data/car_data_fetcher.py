import os
import requests
import json
from typing import Dict
import argparse

class CarDataFetcher:
    def __init__(self, base_url, manufacturer,model, year_from, year_to, page_count, download_photos, save_dir, headers, cookies):
        self.base_url = base_url
        self.manufacturer = manufacturer
        self.model = model
        self.year_from = year_from
        self.year_to = year_to
        self.page_count = page_count
        self.is_download_photos = download_photos
        self.save_dir = save_dir
        self.headers = headers
        self.cookies = cookies
    
    def fetch_from(self, url, headers = None, cookies = None):
        try:
            response = requests.get(url, headers=headers, cookies=cookies)
            response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        except requests.exceptions.RequestException as e:
            print(f"Request failed with exception: {e}")
            return None

        if response.status_code == 200:
            return response
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
        
    def fetch_car_data(self, page):
        params = self.create_query_format(page)
        url = f"{self.base_url}?count=true&q={params['q']}&sr={params['sr']}"

        response = self.fetch_from(url, self.headers, self.cookies)
        if response is not None:
            return response.json()
        return response
    
    def download_photos(self, car_id, photo_urls, save_dir):
        dir_path = f"{save_dir}/{car_id}"
        os.makedirs(dir_path, exist_ok=True)

        for i, url in enumerate(photo_urls):
            response = self.fetch_from(url)
            if response is not None:
                self.save_image(response.content, f"{dir_path}/{i}.jpg")
    
    def prepare_photo_urls(self, single_car_data):
        if not single_car_data or 'Photos' not in single_car_data:
            return []
        
        photo_urls = []
        for photo in single_car_data['Photos']:
            base_url = 'https://ci.encar.com' # TODO: move this to config.py
            photo_urls.append(base_url + photo['location'])
        
        return photo_urls

    def create_query_format(self, page) -> Dict[str, str]:
        params = {
            "count": "true",
            "q": f"(And.Hidden.N._.(C.CarType.Y._.(C.Manufacturer.{self.manufacturer}._.ModelGroup.{self.model}.))_.Year.range({self.year_from}..{self.year_to}).)",
            "sr": f"|PriceAsc|{(page * 10) * 2}|20"
        }
        print(params)
        return params

    def save_image(self, image, filename):
        with open(filename, 'wb') as file:
            file.write(image)

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

                price_krw = int(float(car.get('Price', 0)) * 10000)
                price_with_currency = f"{price_krw} KRW"

                year_as_int = int(car.get('Year', 0))
                mileage_as_int = int(car.get('Mileage', 0))

                all_car_data[id] = {
                    'Manufacturer': car.get('Manufacturer', ''),
                    'Price': price_with_currency,
                    'Model': car.get('Model', ''),
                    'Badge': car.get('Badge', ''),
                    'BadgeDetail': car.get('BadgeDetail', ''),
                    'GreenType': car.get('GreenType', ''),
                    'FuelType': car.get('FuelType', ''),
                    'Year': year_as_int,
                    'Mileage': mileage_as_int,
                    'ServiceCopyCar': car.get('ServiceCopyCar', ''),
                    'OfficeCityState': car.get('OfficeCityState', ''),
                }
                if self.is_download_photos:
                    photo_urls = self.prepare_photo_urls(car)
                    self.download_photos(id, photo_urls, self.save_dir)

        if all_car_data:
            self.save_to_json(all_car_data, output_json_filename)
            self.create_markdown_table(all_car_data, output_md_filename)
        else:
            print("No data fetched or all data was empty.")