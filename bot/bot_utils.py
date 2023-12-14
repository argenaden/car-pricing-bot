import requests
import openai
from bot_config import Config
import json

openai.api_key = Config.OPENAI_API_KEY
telegram_bot_token = Config.TELEGRAM_BOT_TOKEN

def load_car_details():
    with open('data/car_details.json', 'r') as file:
        return json.load(file)

car_details = load_car_details()

def generate_answer(question):
    question_lower = question.lower()
    response = ""

    # for just for testing
    keywords = {
        "kia": "kia",
        "киа": "kia",
        "hyundai": "hyundai",
        "цены": "price",
        "price": "price",
        "mashina": "car",
        "машина": "car"
    }

    relevant_keywords = [value for key, value in keywords.items() if key in question_lower]

    if relevant_keywords:
        for car_id, car in car_details.items():
            if any(car.get("Производитель", "").lower() == keyword for keyword in relevant_keywords):
                model = car.get("Модель", "Model not specified")
                price = car.get("Цена", "Price not available")
                car_info = f"Model: {model}, Price: {price}\n"

                # testing photos
                photo_link = f"https://github.com/argenaden/car-pricing-korea/blob/main/car_photos/{car_id}/3.jpg"
                car_info += f"Photo: {photo_link}\n\n"

                if len(response) + len(car_info) <= 1000:
                    response += car_info
                else:
                    break

        if response:
            return response.strip()
    else:
        response = openai.completions.create(
            model="text-davinci-003",
            prompt=f"Q: {question}\nA:",
            max_tokens=1024,
            temperature=0.7
        )
        return response.choices[0].text.strip()



def keyword_translation(keyword):
    translations = {
        "Model": "Модель",
        "Manufacturer": "Производитель",
        "Price": "Цена",
        "FuelType": "Тип Топлива",
        "OfficeCityState": "Город Офиса"
    }
    return translations.get(keyword, keyword)



def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    return chat_id, text

def send_message_telegram(chat_id, text):
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    return requests.post(url, json=payload)
