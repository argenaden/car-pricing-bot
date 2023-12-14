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
    # Pre-process the user's question to identify keywords
    keywords = []

    if "model" in question.lower():
        keywords.append("Model")
    if "brand" in question.lower():
        keywords.append("Manufacturer")
    if "price" in question.lower():
        keywords.append("Price")
    if "fuel type" in question.lower():
        keywords.append("FuelType")
    if "location" in question.lower():
        keywords.append("OfficeCityState")

    if keywords:
        response = ""

        for car in car_details:
            if car.get("Manufacturer", "").lower() == "기아":
                car_info = ""
                for keyword in keywords:
                    if keyword in car:
                        car_info += f"{keyword}: {car[keyword]}\n"
                car_info += "\n"

                if len(response) + len(car_info) <= 500:
                    response += car_info
                else:
                    break

        if response:
            return response.strip()

    response = openai.completions.create(
        model="text-davinci-003",
        prompt=f"Q: {question}\nA:",
        max_tokens=1024,
        temperature=0.7
    )
    return response.choices[0].text.strip()



def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    return chat_id, text

def send_message_telegram(chat_id, text):
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    return requests.post(url, json=payload)
