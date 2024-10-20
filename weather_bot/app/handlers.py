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

    keyboard = [
                [KeyboardButton('Share location', request_location=True)],
                [KeyboardButton('Get current weather')],
                ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='''Welcome! I'll send you daily weather updates ⛅
                \nSet your location clicking the 'Share location' button below ⬇️ to receive accurate weather updates.
                ''',
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
            text = '''Thanks! Location is set!
                    \nClick /current_weather or the button below ⬇️ to receive current weather information ☔
                    \nDon't forget to change your location if you move somewhere 🌍
                    ''',
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text = "You didn't provide the location 😢 click /setlocation to try again."
        )

async def current_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    message_text = update.message.text

    if message_text == "Get current weather" or message_text == "/current_weather":
        user, created = await sync_to_async(User.objects.get_or_create)(telegram_id=telegram_user.id)

        load_dotenv()
        if user.lat and user.lon:
            api_key = os.getenv("WEATHER_API_KEY")
            current_weather_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric"
            weather = _fetch_current_weather(user.lat, user.lon, api_key, current_weather_url)

            weather_message = (
                "Current weather ☔ \n"
                "\n"
                f"🌡️ Temperature: {weather['temperature']}\n"
                f"🤔 Feels like: {weather['feels like']}\n"
                f"🌦️ Description: {weather['description']}\n"
                "\n"
                f"💨 Wind: {weather['wind']}\n"
                f"🌧️ Rain: {weather['rain']}\n"
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{weather_message}",
            )

def _fetch_current_weather(lat, lon, api_key, current_weather_url):
    response = requests.get(current_weather_url.format(lat, lon, api_key)).json()

    weather_current = {
        "temperature": f"{round(response['main']['temp'])}°C",
        "feels like": f"{round(response['main']['feels_like'])}°C",
        "description": response['weather'][0]['description'],
        "wind": f"{response['wind']['speed']} meter/sec",
        "rain": f"{response.get('rain', {}).get('1h', 0)} mm/h",
    }

    return weather_current