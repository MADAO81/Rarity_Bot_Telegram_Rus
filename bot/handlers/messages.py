"""
Обработчик текстовых сообщений для бота Рарити.

Автор: MADAO81
Версия: 1.0
"""

import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.ai_service import get_rarity_response
from bot.services.weather_service import WeatherService
from bot.utils.time_utils import is_working_hours, get_working_status_message
from bot.core.context_manager import ContextManager

logger = logging.getLogger(__name__)

weather_service = WeatherService()
context_manager = ContextManager()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений."""
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    # Проверка: нужно ли реагировать в группе
    if update.message.chat.type != "private":
        bot_username = context.bot.username
        is_mentioned = False

        if update.message.text and f"@{bot_username}" in update.message.text.lower():
            is_mentioned = True

        if update.message.reply_to_message:
            if update.message.reply_to_message.from_user.username == bot_username:
                is_mentioned = True

        if not is_mentioned:
            return

    status_message = await update.message.reply_text("💎 Думаю...")

    try:
        user_id = update.effective_user.id
        user_message = update.message.text or ""

        # Проверка на погоду
        weather_keywords = ["погода", "weather", "за окном", "температура", "дождь", "солнце", "градус", "ветер"]
        if any(kw in user_message.lower() for kw in weather_keywords):
            patterns = [
                r'во\s+([А-Яа-яA-Za-z\s\-]+?)(?:\s|,|\.|$|\))',
                r'в\s+([А-Яа-яA-Za-z\s\-]+?)(?:\s|,|\.|$|\))',
                r'погода\s+во\s+([А-Яа-яA-Za-z\s\-]+?)(?:\s|,|\.|$|\))',
                r'погода\s+в\s+([А-Яа-яA-Za-z\s\-]+?)(?:\s|,|\.|$|\))',
                r'погода\s+([А-Яа-яA-Za-z\s\-]+?)(?:\s|,|\.|$|\))',
                r'weather\s+in\s+([A-Za-z\s\-]+?)(?:\s|,|\.|$|\))',
            ]

            city_found = None
            for pattern in patterns:
                match = re.search(pattern, user_message, re.IGNORECASE)
                if match:
                    city_found = match.group(1).strip()
                    break

            if city_found and city_found.lower() not in ["ворсино", "боровск"]:
                weather = await weather_service.get_weather_by_city(city_found)
                if weather:
                    weather_text = weather_service.get_weather_text(weather, city_found)
                    response = f"🌤️ *Погода в {city_found}*\n\n{weather_text}"
                else:
                    response = f"😅 Не могу найти город '{city_found}'! 🌧️"
            else:
                weather = await weather_service.get_weather()
                if weather:
                    weather_text = weather_service.get_weather_text(weather)
                    response = f"🌤️ *Погода в Ворсино*\n\n{weather_text}"
                else:
                    response = "😅 Не могу узнать погоду! Попробуй позже! 🌧️"

            await status_message.delete()
            await update.message.reply_text(response, parse_mode="Markdown")
            return

        # Обычный ответ через ИИ
        context_history = context_manager.get_context(user_id)

        response = await get_rarity_response(
            user_message=user_message,
            mood_description="happy",
            context_history=context_history
        )

        if not response:
            response = "😅 Ой-ой! Что-то я задумалась... Давай попробуем ещё раз? 💎"

        await status_message.delete()

        if update.message.chat.type == "private":
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(
                response,
                reply_to_message_id=update.message.message_id
            )

        context_manager.save_context(user_id, user_message, response)

    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения: {e}")
        await status_message.edit_text(
            "😅 Упс! Что-то пошло не так!\n"
            "Попробуй ещё раз или напиши /help для справки! 💎"
        )
