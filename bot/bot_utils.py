import requests
import openai
from bot_config import Config

openai.api_key = Config.OPENAI_API_KEY
telegram_bot_token = Config.TELEGRAM_BOT_TOKEN


def load_car_details():
    with open('car_details.json', 'r') as file:
        return json.load(file)

def generate_answer(question):
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
