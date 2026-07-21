import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.ai_service import analyze_image
from bot.utils.time_utils import is_working_hours

logger = logging.getLogger(__name__)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        return
    await update.message.reply_text("🖼️ Ой, какая красивая картинка! 💎")
    # Здесь можно добавить анализ через Vision API
