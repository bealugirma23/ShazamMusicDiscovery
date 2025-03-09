import os
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters, ApplicationBuilder
from dotenv import load_dotenv
from bot.logging_config import setup_logging
from bot.handlers import start, recognize ,top, help, query_handler, unknown, search

load_dotenv()

def main():
    setup_logging()  # Initialize the logger
    print("Starting the bot...")
    token = os.getenv('TOKEN')
    print(token)
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("top", top))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CallbackQueryHandler(query_handler))
    application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, recognize))
    application.add_handler(MessageHandler(filters.TEXT, search))

    application.add_handler(MessageHandler(filters.COMMAND | filters.TEXT, unknown))

    application.run_polling()

if __name__ == "__main__":
    main()