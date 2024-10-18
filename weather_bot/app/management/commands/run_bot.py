import asyncio
import os
import logging
import django
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, filters)

from app.handlers import start, set_location, location_handler, current_weather



class Command(BaseCommand):
    help = "Runs the Telegram bot"

    def handle(self, *args, **kwargs):
        load_dotenv()
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "weather_bot.settings")
        django.setup()

        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

        asyncio.run(self.run_bot())

    def run_bot(self):

        application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("setlocation", set_location))
        application.add_handler(MessageHandler(filters.LOCATION, location_handler))
        application.add_handler(CommandHandler("current_weather", current_weather))

        application.run_polling()