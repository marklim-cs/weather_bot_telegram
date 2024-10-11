from django.shortcuts import render
from dotenv import load_dotenv
import datetime
import os

def index(request):
    API_KEY = os.getenv("API_KEY")

    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
    forecast_today_url = "http://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"