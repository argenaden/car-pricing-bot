from typing import Dict
from car_data_fetcher import CarDataFetcher
from config import headers, cookies
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch and save car data.")
    parser.add_argument("--manufacturer", type=str, default="기아", help="Manufacturer name")
    parser.add_argument("--category", type=str, default="경차", help="Car category")
    parser.add_argument("--year_from", type=str, default="201400", help="Starting year")
    parser.add_argument("--year_to", type=str, default="202399", help="Ending year")
    parser.add_argument("--page_count", type=int, default=10, help="Number of pages to fetch")
    parser.add_argument("--download_photos", action="store_true", help="Download photos")
    parser.add_argument("--save_dir", type=str, default="car_photos", help="Directory to save photos")
    return parser.parse_args()

def main():
    args = parse_arguments()
    base_url = 'https://api.encar.com/search/car/list/premium'

    car_data_fetcher = CarDataFetcher(
        base_url, 
        args.manufacturer, 
        args.category, 
        args.year_from, 
        args.year_to, 
        args.page_count,
        args.download_photos, 
        args.save_dir, 
        headers, 
        cookies
    )

    car_data_fetcher.fetch_and_save_data('car_details.json', 'car_details.md')

if __name__ == "__main__":
    main()
