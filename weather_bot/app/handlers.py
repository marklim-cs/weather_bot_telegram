import os
import datetime
from collections import defaultdict
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from dotenv import load_dotenv

from .models import User

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user

    await sync_to_async(User.objects.get_or_create)(
        telegram_id=telegram_user.id,
        defaults = {'name': telegram_user.full_name}
    )

    keyboard = [
                [KeyboardButton("Share location", request_location=True)],
                [KeyboardButton("Get current weather")],
                [KeyboardButton("Today's weather")],
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
            text = "You didn't provide the location 😢 click 'Share location' button to try again."
        )

async def current_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    message_text = update.message.text

    if message_text == "Get current weather" or message_text == "/current_weather":
        user, created = await sync_to_async(User.objects.get_or_create)(telegram_id=telegram_user.id)

        load_dotenv()
        if user.lat and user.lon:
            current_weather_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric"
            weather = _fetch_current_weather(user.lat, user.lon, API_KEY, current_weather_url)

            weather_message = (
                "Current weather ☔ \n"
                "\n"
                f"🌡️ Temperature: {weather['temperature']}\n"
                f"🤔 Feels like: {weather['feels_like']}\n"
                f"🌦️ Description: {weather['description']}\n"
                "\n"
                f"💨 Wind: {weather['wind']}\n"
                f"🌧️ Rain: {weather['rain']}\n"
            )

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{weather_message}",
            )

async def todays_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    message_text = update.message.text

    if message_text == "Today's weather":
        user, created = await sync_to_async(User.objects.get_or_create)(telegram_id = telegram_user.id)

        if user.lat and user.lon:
            forecast_weather_url = "http://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"
            weather_f = _fetch_weather_forecast(user.lat, user.lon, API_KEY, forecast_weather_url)

            weather_message = (
                "Today's weather ☔ \n"
                    "\n"
                    f"🌡️ Min. temperature: {weather_f['min_temp']}\n"
                    f"🌡️ Max. temperature: {weather_f['max_temp']}\n"
                    f"🌦️ Description: {weather_f['description']}\n"
            )

            await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"{weather_message}",
                )

def _fetch_current_weather(lat, lon, api_key, current_weather_url):
    try:
        response = requests.get(current_weather_url.format(lat, lon, api_key),
                            timeout=10).json()
    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later."

    weather_current = {
        "temperature": f"{round(response['main']['temp'])}°C",
        "feels_like": f"{round(response['main']['feels_like'])}°C",
        "description": response['weather'][0]['description'],
        "wind": f"{response['wind']['speed']} meter/sec",
        "rain": f"{response.get('rain', {}).get('1h', 0)} mm/h",
    }

    return weather_current

def _fetch_weather_forecast(lat, lon, api_key, forecast_weather_url):
    try:
        response = requests.get(forecast_weather_url.format(lat, lon, api_key),
                            timeout=10).json()
    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later."

    daily_forecast = []
    daily_data_grouped = defaultdict(list)

    #group the data by day
    for daily_data in response['list'][0:40]:
        day = datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A")
        daily_data_grouped[day].append(daily_data)

    #exctract min and max temp
    for day, data_list in list(daily_data_grouped.items())[0:1]:
        min_temp = round(min(data['main']['temp'] for data in data_list))
        max_temp = round(max(data['main']['temp'] for data in data_list))

        descriptions = (data['weather'][0]['description'] for data in data_list)
        most_frequent_description = count_element_frequency(descriptions)

        icons = (data['weather'][0]['icon'] for data in data_list)
        most_frequent_icon = count_element_frequency(icons)

        daily_forecast.append({
            "day": day, 
            "min_temp": min_temp, 
            "max_temp": max_temp,
            "description": most_frequent_description,
            "icon": most_frequent_icon,
        })

        return daily_forecast

def count_element_frequency(array):
    frequency_dict = {}

    for element in array:
        if element in frequency_dict:
            frequency_dict[element] += 1
        else:
            frequency_dict[element] = 1

    max_key = max(frequency_dict, key=frequency_dict.get)
    return max_key