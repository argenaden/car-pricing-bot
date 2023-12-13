from flask import Blueprint, request, Response
from bot_utils import message_parser, generate_answer, send_message_telegram

main = Blueprint('main', __name__)

@main.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, incoming_que = message_parser(msg)
        answer = generate_answer(incoming_que)
        send_message_telegram(chat_id, answer)
        return Response('ok', status=200)
    else:
        return "<h1>Welcome to the webhook!</h1>"

@main.route('/', methods=['GET', 'POST'])
def index():
    return "<h1>Telegram Bot Webhook Endpoint</h1>"
