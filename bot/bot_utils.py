import requests
import openai
import json
import os
from bot_config import Config

openai.api_key = Config.OPENAI_API_KEY
telegram_bot_token = Config.TELEGRAM_BOT_TOKEN


def load_car_details():
    json_file_path = os.path.join(os.path.dirname(__file__), 'data', 'car_details.json')
    with open(json_file_path, 'r') as file:
        return json.load(file)


car_details = load_car_details()

keywords = {
    "kia": "kia",
    "киа": "киа",
    "hyundai": "hyundai",
    "цены": "price",
    "price": "price",
    "mashina": "car",
    "машина": "car"
}


def get_car_attribute(car, attribute):
    keys_map = {
        'manufacturer': ['Производитель', 'Manufacturer'],
        'price': ['Цена', 'Price'],
        'model': ['Модель', 'Model'],
        'fuel_type': ['Тип Топлива', 'FuelType'],
        'office_city_state': ['Город Офиса', 'OfficeCityState']
    }
    for key in keys_map.get(attribute, []):
        if key in car:
            return car[key]
    return None


def generate_answer(question):
    if question is None:
        return "Sorry, I can only respond to text messages."

    print(f"Processing question: {question}")  # Debug output
    question_lower = question.lower()
    relevant_keywords = [value for key, value in keywords.items() if key in question_lower]
    print(f"Relevant keywords: {relevant_keywords}")  # Debug output

    if relevant_keywords:
        responses = []

        for car_id, car in car_details.items():
            manufacturer = get_car_attribute(car, 'manufacturer')
            if any(keyword in manufacturer.lower() for keyword in relevant_keywords):
                model = get_car_attribute(car, 'model') or "Model not specified"
                price = get_car_attribute(car, 'price') or "Price not available"
                fuel_type = get_car_attribute(car, 'fuel_type') or "Fuel type not specified"
                office_city_state = get_car_attribute(car, 'office_city_state') or "Office location not specified"
                car_info = f"Model: {model}, Price: {price}, Fuel Type: {fuel_type}, Location: {office_city_state}"
                photo_url = f"https://raw.githubusercontent.com/argenaden/car-pricing-korea/main/car_photos/{car_id}/2.jpg"
                responses.append((photo_url, car_info))
                print(f"Generated car info: {car_info}")

                if len(responses) >= 5:
                    break

        return responses

    else:
        try:
            context = "У меня вопрос про автомобили в Корее"
            response = openai.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=f"{context}\nQ: {question}\nA:",
                max_tokens=1024,
                temperature=0.7
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")  # Error handling
            return "There was an error processing your request. Please try again."


def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message.get('message', {}).get('text')
    return chat_id, text


def send_message_telegram(chat_id, text):
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    return requests.post(url, json=payload)


def send_photo_telegram(chat_id, photo_url, caption):
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendPhoto'
    payload = {
        'chat_id': chat_id,
        'photo': photo_url,
        'caption': caption
    }
    return requests.post(url, json=payload)


def handle_incoming_message(message):
    chat_id, incoming_question = message_parser(message)
    if incoming_question:
        responses = generate_answer(incoming_question)

        if isinstance(responses, list):
            for photo_url, caption in responses:
                send_photo_telegram(chat_id, photo_url, caption)
        else:
            send_message_telegram(chat_id, responses)
    else:

        send_message_telegram(chat_id, "I received a non-text message which I cannot process.")
