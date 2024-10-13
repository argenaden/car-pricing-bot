import os
import argparse
import json
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

YEAR_RANGE_START = 2018
YEAR_RANGE_END = 2024

# Define conversation states
MANUFACTURER, MODEL, START_YEAR, END_YEAR, LOCATION, BIO = range(6)

# Dictionary of car manufacturers and models
CAR_DICT = {
    'Hyundai': ['Grandeur', 'Avante', 'Sonata', 'Santa Fe', 'Starex', 'Tucson'],
    'KIA': ['Carnival', 'K5', 'K7', 'Sorento', 'Ray', 'Morning'],
    'Genesis': ['EQ900', 'G70', 'G80', 'G90', 'GV70', 'GV80', 'GV90'],
    'Chevrolet': ['Spark', 'Malibu', 'Trax', 'Cruze', 'Orlando', 'Trailblazer'],
}

ENG2KOR_MAP = {'Hyundai': '현대', 'KIA': '기아', 'Genesis': '제네시스', 'Chevrolet': '쉐보레',
               'Grandeur': '그랜저', 'Avante': '아반떼', 'Sonata': '소나타', 'Santa Fe': '산타페',
               'Starex': '스타렉스', 'Tucson': '투싼', 'Carnival': '카니발', 'K5': 'K5', 'K7': 'K7',
               'Sorento': '쏘렌토', 'Ray': '레이', 'Morning': '모닝', 'EQ900': 'EQ900', 'G70': 'G70',
               'G80': 'G80', 'G90': 'G90', 'GV70': 'GV70', 'GV80': 'GV80', 'GV90': 'GV90',
               'Spark': '스파크', 'Malibu': '말리부', 'Trax': '트랙스', 'Cruze': '크루즈',
               'Orlando': '올란도', 'Trailblazer': '트레일블레이저'}

KOR2ENG_MAP = {'디젤': 'Diesel', '가솔린': 'Gasoline', '수동': 'Manual', '자동': 'Automatic'}

# Start the conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about the manufacturer."""
    reply_keyboard = [[mnfctr] for mnfctr in CAR_DICT.keys()]

    await update.message.reply_text(
        "Здравствуйте! Я умный бот, я помогу вам найти автомобиль. Какая марка автомобиля вас интересует?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MANUFACTURER

# Handle manufacturer selection
async def manufacturer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected manufacturer and asks for a model."""
    user = update.message.from_user
    mnfctr = update.message.text

    if mnfctr not in CAR_DICT:
        await update.message.reply_text("Пожалуйста, выберите марку автомобиля с клавиатуры.")
        return MANUFACTURER

    context.user_data['manufacturer'] = mnfctr
    logger.info(f"User {user.first_name} is interested in {mnfctr} cars.")

    # Create a dynamic keyboard for selecting the model
    reply_keyboard = [[mdl] for mdl in CAR_DICT[mnfctr]]

    await update.message.reply_text(
        f"Вы выбрали {mnfctr}. Теперь выберите модель автомобиля:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return MODEL

# Handle model selection
async def model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected model and asks for the preferred start year."""
    user = update.message.from_user
    model = update.message.text
    mnfctr = context.user_data.get('manufacturer')

    if model not in CAR_DICT[mnfctr]:
        await update.message.reply_text("Пожалуйста, выберите модель автомобиля с клавиатуры.")
        return MODEL

    context.user_data['model'] = model
    logger.info(f"User {user.first_name} selected {model} model from {mnfctr}.")

    # Create a dynamic keyboard for selecting the start year
    reply_keyboard = [[str(year)] for year in range(YEAR_RANGE_START, YEAR_RANGE_END + 1)]

    await update.message.reply_text(
        f"Вы выбрали {mnfctr} {model}. Теперь выберите начальный год диапазона (например, 2020):",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

    return START_YEAR

# Handle start year selection
async def start_year_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the start year selection and asks for the end year."""
    user = update.message.from_user
    try:
        start_year = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите год в числовом формате.")
        return START_YEAR

    if start_year < YEAR_RANGE_START or start_year > YEAR_RANGE_END:
        await update.message.reply_text(f"Пожалуйста, выберите год в диапазоне от {YEAR_RANGE_START} до {YEAR_RANGE_END}.")
        return START_YEAR
    
    context.user_data['start_year'] = start_year
    logger.info(f"User {user.first_name} selected {start_year} as the start year.")

    # Create a dynamic keyboard for selecting the end year
    reply_keyboard = [[str(year)] for year in range(start_year, YEAR_RANGE_END + 1)]

    await update.message.reply_text(
        f"Вы выбрали {start_year} как начальный год. Теперь выберите конечный год:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

    return END_YEAR

# Handle end year selection
async def end_year_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the end year selection and asks for the location."""
    user = update.message.from_user
    try:
        end_year = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите год в числовом формате.")
        return END_YEAR

    start_year = context.user_data['start_year']
    if end_year < start_year or end_year > YEAR_RANGE_END:
        await update.message.reply_text(f"Пожалуйста, выберите год в диапазоне от {start_year} до {YEAR_RANGE_END}.")
        return END_YEAR

    # Retrieve data_path from context.application_data
    # data_path = context.application_data['data_path']
    data_path = "/Users/kanybekasanbekov/projects/car-pricing-korea/data/hyundai.json"

    context.user_data['end_year'] = int(end_year)
    mnfctr = context.user_data['manufacturer']
    model = context.user_data['model']
    start_year = context.user_data['start_year']
    end_year = context.user_data['end_year']

    await update.message.reply_text(f"Вы выбрали {mnfctr} {model} с {start_year} по {end_year} года выпуска.")

    with open(data_path, 'r') as file:
        car_database = json.load(file)
    
    num_answers = 0
    for car_id, car_info in car_database.items():
        if ENG2KOR_MAP[mnfctr] == car_info['Manufacturer'] and ENG2KOR_MAP[model] in car_info['Model']:
            year = int(str(car_info['Year'])[:4])
            if start_year <= year <= end_year:
                num_answers += 1

                answer_msg = f"Вариант №{num_answers}\n"
                answer_msg += f"Марка: {mnfctr}\n"
                answer_msg += f"Модель: {model}\n"
                answer_msg += f"Год выпуска: {year}\n"
                answer_msg += f"Пробег: {car_info['Mileage']} км\n"
                answer_msg += f"Топливо: {KOR2ENG_MAP[car_info['FuelType']]}\n"
                answer_msg += f"Цена: {car_info['Price']}\n"
                answer_msg += f"Ссылка: {car_info['URL']}\n"
                # await query.message.reply_text(answer_msg)
                await update.message.reply_text(answer_msg)
                if num_answers == 5:
                    break
    
    if num_answers == 0:
        # await query.edit_message_text("Извините, но я не могу найти автомобиль по вашему запросу.")
        await update.message.reply_text("Извините, но я не могу найти автомобиль по вашему запросу.")

    # await update.callback_query.message.reply_text(
    await update.message.reply_text(
        "Спасибо за использование нашего бота! Если хотите попробовать ещё раз, нажмите /start."
    )
    return ConversationHandler.END

# Cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.first_name} canceled the conversation.")

    await update.message.reply_text(
        "Пока! Надеюсь, мы сможем пообщаться ещё.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Main function to start the bot
def main(data_path) -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("TELEGRAM_TOKEN").build()

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MANUFACTURER: [MessageHandler(filters.TEXT, manufacturer)],
            MODEL: [MessageHandler(filters.TEXT, model)],
            START_YEAR: [MessageHandler(filters.TEXT, start_year_selection)],
            END_YEAR: [MessageHandler(filters.TEXT, end_year_selection)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add the handler to the application
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

def parse_args():
    parser = argparse.ArgumentParser(description="Run the Telegram bot.")
    parser.add_argument("--data_path", type=str, default="data", help="Path car database")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.data_path)
