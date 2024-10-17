from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from app.models import User
from asgiref.sync import sync_to_async

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user

    await sync_to_async(User.objects.get_or_create)(
        telegram_id=telegram_user.id,
        defaults={'name': telegram_user.full_name}
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome! I'll send you daily weather updates. Please set your location using /setlocation.")