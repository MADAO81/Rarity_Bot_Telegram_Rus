import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.utils.time_utils import is_working_hours

logger = logging.getLogger(__name__)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        return
    await update.message.reply_text("🎧 Слушаю тебя... 💎")
    # Здесь можно добавить транскрипцию через Whisper
