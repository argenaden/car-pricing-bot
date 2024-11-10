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
from telegram.constants import ParseMode


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_API_KEY = os.environ["TELEGRAM_BOT_API_KEY"]
YEAR_RANGE_START = 2018
YEAR_RANGE_END = 2024

# Define conversation states
MANUFACTURER, MODEL, START_YEAR, END_YEAR, RETURN_RESULTS = range(5)

# Dictionary of car manufacturers and models
CAR_DICT = {
    'Hyundai': ['Grandeur', 'Avante', 'Sonata', 'Santa Fe', 'Starex', 'Tucson'],
    'KIA': ['Carnival', 'K5', 'K7', 'Sorento', 'Ray', 'Morning'],
    'Genesis': ['EQ900', 'G70', 'G80', 'G90', 'GV70', 'GV80', 'GV90'],
    'Chevrolet': ['Spark', 'Malibu', 'Trax', 'Cruze', 'Orlando', 'Trailblazer'],
}


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

    context.user_data['end_year'] = int(end_year)
    mnfctr = context.user_data['manufacturer']
    model = context.user_data['model']
    start_year = context.user_data['start_year']
    end_year = context.user_data['end_year']

    await update.message.reply_text(f"Вы выбрали {mnfctr} {model} с {start_year} по {end_year} года выпуска.")

    context, answer_msg = search_results(context)

    reply_keyboard = [['Смотреть следующий вариант'], ['Завершить']]
    await update.message.reply_text(answer_msg, parse_mode=ParseMode.MARKDOWN_V2, 
                                    reply_markup=ReplyKeyboardMarkup(
                                        reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    
    return RETURN_RESULTS

# Return the results according to the user's selection
async def return_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_reply = update.message.text
    if user_reply == 'Завершить':
        await update.message.reply_text(
            "Спасибо за использование нашего бота! Если хотите попробовать ещё раз, нажмите /start.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    print(context.bot_data['iter_idx'])
    print(context.bot_data['answer_id'])
    context, answer_msg = search_results(context)

    reply_keyboard = [['Смотреть следующий вариант'], ['Завершить']]
    await update.message.reply_text(answer_msg, parse_mode=ParseMode.MARKDOWN_V2, 
                                    reply_markup=ReplyKeyboardMarkup(
                                        reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    
    return RETURN_RESULTS

# Search the results based on the user's selection
def search_results(context: ContextTypes.DEFAULT_TYPE) -> int:
    mnfctr = context.user_data['manufacturer']
    model = context.user_data['model']
    start_year = context.user_data['start_year']
    end_year = context.user_data['end_year']

    # Retrieve data_path from the application context
    data_path = context.bot_data['data_path']
    with open(data_path, 'r') as file:
        car_database = json.load(file)
    car_database_list = list(car_database.values())
    
    answer_id = context.bot_data['answer_id']
    curr_iter_idx = context.bot_data['iter_idx']
    for i, car_info in enumerate(car_database_list[curr_iter_idx:]):
        if mnfctr == car_info['Manufacturer'] and model in car_info['Model']:
            year = int(str(car_info['Year'])[:4])
            if start_year <= year <= end_year:
                answer_msg = f'__*Вариант №{answer_id}\n*__'
                answer_msg += car_info['short_answer_msg']
                context.bot_data['answer_id'] += 1
                context.bot_data['iter_idx'] = curr_iter_idx + i + 1
                return context, answer_msg


# Cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.first_name} canceled the conversation.")

    await update.message.reply_text(
        "Спасибо за использование нашего бота! Если хотите попробовать ещё раз, нажмите /start.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Main function to start the bot
def main(data_path) -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_API_KEY).build()

    # Store data_path in application context
    if not os.path.isfile(data_path) or not data_path.endswith('.json'):
        raise ValueError("Invalid data path. Please provide a valid JSON file.")
    application.bot_data['data_path'] = data_path
    application.bot_data['answer_id'] = 1
    application.bot_data['iter_idx'] = 0

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MANUFACTURER: [MessageHandler(filters.TEXT, manufacturer)],
            MODEL: [MessageHandler(filters.TEXT, model)],
            START_YEAR: [MessageHandler(filters.TEXT, start_year_selection)],
            END_YEAR: [MessageHandler(filters.TEXT, end_year_selection)],
            RETURN_RESULTS: [MessageHandler(filters.TEXT, return_results)],
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
