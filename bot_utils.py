import requests
import openai
from bot_config import openai_api_key, telegram_bot_token

openai.api_key = openai_api_key

def load_car_details():
    with open('car_details.json', 'r') as file:
        return json.load(file)

# TODO:  Logic to find car details based on a question
# just ex
def find_car_details(question, car_data):
    # price, model and bashka bashka
    return "example"



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
