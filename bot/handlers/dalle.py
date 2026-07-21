import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.ai_service import generate_image, get_rarity_response
from bot.utils.time_utils import is_working_hours, get_working_status_message

logger = logging.getLogger(__name__)

async def dalle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "🎨 *Как создать изображение:*\n\n"
            "`/dalle описание того, что ты хочешь увидеть`\n\n"
            "Например:\n"
            "`/dalle элегантное вечернее платье из бархата`\n"
            "`/dalle принт для ткани с геометрическим узором`",
            parse_mode="Markdown"
        )
        return

    prompt = " ".join(args)
    status_message = await update.message.reply_text("🎨 Думаю над твоим образом...")

    try:
        logger.info(f"🔍 Запрос к Рарити: {prompt[:50]}...")
        
        # Временно: вместо картинки — текстовое описание
        response = await get_rarity_response(
            user_message=f"Пользователь хочет создать изображение: {prompt}. Ты не можешь показать картинку, но можешь подробно описать, как это будет выглядеть: цвета, текстуры, детали. Сделай описание вдохновляющим и детальным.",
            mood_description="happy"
        )
        
        if response:
            await status_message.delete()
            await update.message.reply_text(
                f"💎 *Твой образ от Рарити!*\n\n📝 *Описание:*\n{response}",
                parse_mode="Markdown"
            )
        else:
            await status_message.edit_text("😅 Ой! Что-то пошло не так. Попробуй ещё раз! 💎")
            
    except Exception as e:
        logger.error(f"❌ Ошибка в dalle_command: {e}")
        await status_message.edit_text("😅 Ой! Моя кисточка сломалась! Попробуй позже! 💎")

async def print_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "🖼️ *Как создать принт для ткани:*\n\n"
            "`/print описание узора`\n\n"
            "Например:\n"
            "`/print цветочный принт в стиле бохо`\n"
            "`/print геометрический узор в синих тонах`",
            parse_mode="Markdown"
        )
        return

    prompt = " ".join(args)
    status_message = await update.message.reply_text("🖼️ Придумываю принт для ткани...")

    try:
        logger.info(f"🔍 Запрос на принт: {prompt[:50]}...")
        
        response = await get_rarity_response(
            user_message=f"Пользователь хочет принт для ткани: {prompt}. Ты не можешь показать картинку, но можешь подробно описать узор, цвета, композицию. Сделай описание вдохновляющим.",
            mood_description="happy"
        )
        
        if response:
            await status_message.delete()
            await update.message.reply_text(
                f"🖼️ *Принт для ткани от Рарити!*\n\n📝 *Описание:*\n{response}",
                parse_mode="Markdown"
            )
        else:
            await status_message.edit_text("😅 Ой! Что-то пошло не так. Попробуй ещё раз! 💎")
            
    except Exception as e:
        logger.error(f"❌ Ошибка в print_command: {e}")
        await status_message.edit_text("😅 Ой! Моя кисточка сломалась! Попробуй позже! 💎")
