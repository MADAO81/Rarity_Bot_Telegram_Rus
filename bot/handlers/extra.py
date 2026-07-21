import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.ai_service import get_rarity_response
from bot.utils.time_utils import is_working_hours, get_working_status_message

logger = logging.getLogger(__name__)

async def style_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    query = " ".join(args) if args else "совет по стилю"

    status_message = await update.message.reply_text("👗 Дай-ка подумать о твоём стиле...")

    try:
        response = await get_rarity_response(
            user_message=f"Пользователь просит совет по стилю: {query}. Дай элегантный, персонализированный совет. Говори как Рарити — изящно, с драматизмом, вдохновляюще. Используй эмодзи.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"👗 *Совет от Рарити:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("😅 Ой! Я не смогла подобрать совет... Попробуй ещё раз! 💎")
    except Exception as e:
        logger.error(f"❌ Style error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")

async def craft_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    query = " ".join(args) if args else "идею для рукоделия"

    status_message = await update.message.reply_text("🧵 Сейчас придумаю что-то прекрасное...")

    try:
        response = await get_rarity_response(
            user_message=f"Пользователь просит идею для рукоделия: {query}. Предложи вдохновляющую идею (пэчворк, шитьё, вышивка, мозаика, картины по номерам). Говори как Рарити.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"🧵 *Идея от Рарити:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("😅 Ой! Я не смогла придумать идею... Попробуй ещё раз! 💎")
    except Exception as e:
        logger.error(f"❌ Craft error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")

async def repair_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    query = " ".join(args) if args else "ремонт одежды"

    status_message = await update.message.reply_text("🪡 Сейчас подберу хороший совет...")

    try:
        response = await get_rarity_response(
            user_message=f"Пользователь просит совет по ремонту одежды: {query}. Дай практичный, понятный совет (как зашить, подшить, пришить пуговицу). Говори как Рарити.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"🪡 *Совет от Рарити:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("😅 Ой! Я не смогла подобрать совет... Попробуй ещё раз! 💎")
    except Exception as e:
        logger.error(f"❌ Repair error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")

async def inspire_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    status_message = await update.message.reply_text("✨ Сейчас я вдохновлю тебя...")

    try:
        response = await get_rarity_response(
            user_message="Дай вдохновляющую фразу, цитату или идею о красоте, творчестве или гармонии. Говори как Рарити — изящно, с душой, вдохновляюще.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"✨ *Вдохновение от Рарити:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("💎 Красота вокруг нас! 💎")
    except Exception as e:
        logger.error(f"❌ Inspire error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")
