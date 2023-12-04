import requests
import json

def fetch_car_data(url, headers, cookies):
    response = requests.get(url, headers=headers, cookies=cookies)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed with status code {response.status_code}")
        return None

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def create_markdown_table(data, md_filename):
    headers = data[0].keys()
    md_table = "| " + " | ".join(headers) + " |\n"  # Table header
    md_table += "| " + " | ".join(["-" * len(h) for h in headers]) + " |\n"  # Separator

    for entry in data:
        row = "| " + " | ".join(str(entry.get(h, '')) for h in headers) + " |"
        md_table += row + "\n"

    with open(md_filename, 'w', encoding='utf-8') as file:
        file.write(md_table)

def main():
    url = 'http://api.encar.com/search/car/list/general?count=true&q=(And.(And.Hidden.N._.(C.CarType.Y._.(C.Manufacturer.%ED%98%84%EB%8C%80._.ModelGroup.%EA%B7%B8%EB%9E%9C%EC%A0%80.)))_.Trust.Warranty.)&sr=%7CExtendWarranty%7C0%7C5'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en,ko;q=0.9,tr;q=0.8,ru;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'api.encar.com',
        'Origin': 'http://www.encar.com',
        'Referer': 'http://www.encar.com/',
    }
    cookies = {
        '_encar_hostname': 'http://www.encar.com',
        'cto_bundle': '1N4SLF9qdWE1Yk5hY3dicmtjeDZqWnFxcnFjd3BpRmVJSkMlMkZsdkV0azk4ZERYYU9ZdjNSSEtLaWFoTlhJbWwwSnBLVGoyMiUyRnI0NG82SnlHd3RpMG5oVXRxMGx3VXRMJTJCTzdvTkZBczQxVFJiZ1JCU3I1c2R4M1F5RWZ0QUp3WVVXRU1WaTE5N3oyJTJGRzRlbkFMd0NoJTJGcDI4REk3Skt4M2dUaXFpZjJ4ZzZDMkVXeGhRcVUlMkJpeXEwaHlLQUh1NjdFVmcxemtiMU1BcVgxV0k3dnVnJTJGYm5yQUhTWVElM0QlM0Q',
        'AF_SYNC': '1701652523853',
        '_ga_BQ7RK9J6BZ': 'GS1.1.1701674727.5.0.1701674727.60.0.0',
        'JSESSIONID': 'VD4cbokASjVgSa7OPIVh4XHHlDwaXdqpLc8QkMs6ZdLNPeqXnvD81RO09tckTWN3.mono-was2-prod_servlet_encarWeb5',
        'WMONID': '5bPyRCUPVzy'
    }

    raw_data = fetch_car_data(url, headers, cookies)
    if raw_data:
        car_data = [ {
            'Manufacturer': car.get('Manufacturer', ''),
            'Model': car.get('Model', ''),
            'Badge': car.get('Badge', ''),
            'BadgeDetail': car.get('BadgeDetail', ''),
            'GreenType': car.get('GreenType', ''),
            'FuelType': car.get('FuelType', ''),
            'Year': car.get('Year', ''),
            'FormYear': car.get('FormYear', ''),
            'Mileage': car.get('Mileage', ''),
            'ServiceCopyCar': car.get('ServiceCopyCar', ''),
            'Price': car.get('Price', ''),
            'OfficeCityState': car.get('OfficeCityState', '')
        } for car in raw_data.get('SearchResults', [])]

        save_to_json(car_data, 'car_details.json')

        json_filename = 'car_details.json'
        md_filename = 'car_details.md'

        car_data = load_json(json_filename)
        create_markdown_table(car_data, md_filename)

if __name__ == "__main__":
    main()
