from flask import request, Response
from bot_utils import generate_answer, message_parser, send_message_telegram

def init_routes(app):
    @app.route('/webhook', methods=['POST'])
    def webhook():
        msg = request.get_json()
        chat_id, incoming_question = message_parser(msg)
        answer = generate_answer(incoming_question)
        send_message_telegram(chat_id, answer)
        return Response('OK', status=200)

    @app.route('/', methods=['GET'])
    def index():
        return "<h1>Telegram Bot Webhook Endpoint</h1>"
