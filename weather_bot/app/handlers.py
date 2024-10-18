import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async

from .models import User


logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user

    await sync_to_async(User.objects.get_or_create)(
        telegram_id=telegram_user.id,
        defaults = {'name': telegram_user.full_name}
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome! I'll send you daily weather updates. Please set your location using /setlocation.")

async def set_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton('Share location', request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please share your location by clicking the button below to receive accurate weather updates.",
        reply_markup = reply_markup,
    )

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    location = update.message.location

    if location:

        user, created = await sync_to_async(User.objects.get_or_create)(telegram_id=telegram_user.id)

        if user.lat is None or user.lon is None:
            user.lat = location.latitude
            user.lon = location.longitude

            await sync_to_async(user.save)()

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = f"Thanks!\nYour location:\nLatitude {user.lat}\nLongtitude {user.lon}",
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = "You didn't provide the location :/ click /setlocation to try again"
        )