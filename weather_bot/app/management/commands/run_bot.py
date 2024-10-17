import asyncio
import os
import logging
import django
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler
)
from app.handlers import start

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

        application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
        application.add_handler(CommandHandler("start", start))

        asyncio.run(application.run_polling())