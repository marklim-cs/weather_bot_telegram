import os
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from dotenv import load_dotenv

from .models import User

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
    keyboard = [
                [KeyboardButton('Share location', request_location=True)],
                [KeyboardButton('Get current weather')]
                ]
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
            text = "Thanks! Location is set.\n Click /current_weather to receive current weather information",
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = "You didn't provide the location :/ click /setlocation to try again"
        )

async def current_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user

    user, created = await sync_to_async(User.objects.get_or_create)(telegram_id=telegram_user.id)

    load_dotenv()
    if user.lat and user.lon:
        api_key = os.getenv("WEATHER_API_KEY")
        current_weather_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric"
        weather = _fetch_current_weather(user.lat, user.lon, api_key, current_weather_url)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = f"{weather}"
        )

def _fetch_current_weather(lat, lon, api_key, current_weather_url):
    response = requests.get(current_weather_url.format(lat, lon, api_key)).json()

    #weather_current = {
        #"temperature": round(response['main']['temp']),
        #"feels like": response['main']['feels_like'],
        #"description": response['weather'][0]['description'],
        #"wind": response['wind']['speed'],
        #"rain": response['rain']['1h'],
    #}

    return response