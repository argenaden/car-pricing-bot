from typing import Dict
from data.car_data_fetcher import CarDataFetcher
from config.settings import HEADERS, COOKIES
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Fetch and save car data.")
    parser.add_argument("--manufacturer", type=str, default="현대", help="Manufacturer name")
    parser.add_argument("--model", type=str, default="아반떼", help="Model name")
    parser.add_argument("--year_from", type=str, default="201253", help="Starting year")
    parser.add_argument("--year_to", type=str, default="202412", help="Ending year")
    parser.add_argument("--page_count", type=int, default=20, help="Number of pages to fetch")
    parser.add_argument("--download_photos", action="store_true", help="Download photos")
    parser.add_argument("--save_dir", type=str, default="car_photos", help="Directory to save photos")
    return parser.parse_args()

def main():
    args = parse_arguments()

    car_data_fetcher = CarDataFetcher(
        args.manufacturer,
        args.model,
        args.year_from, 
        args.year_to, 
        args.page_count,
        args.download_photos, 
        args.save_dir, 
        HEADERS,
        COOKIES
    )

    car_data_fetcher.fetch_and_save_data('data/hyundai.json', 'data/hyundai.md')

if __name__ == "__main__":
    main()
