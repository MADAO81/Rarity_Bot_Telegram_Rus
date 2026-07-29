import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.ai_service import analyze_image
from bot.utils.time_utils import is_working_hours
from bot.core.context_manager import ContextManager

logger = logging.getLogger(__name__)

context_manager = ContextManager()


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles photos."""
    logger.info("📸 FUNCTION handle_photo CALLED!")

    if not is_working_hours():
        logger.info("⏰ Not working hours, photo ignored")
        return

    status_message = await update.message.reply_text("🖼️ Looking at the picture... Let me think!")

    try:
        user_id = update.effective_user.id
        user_message = update.message.caption or "Nice picture!"

        photo_file = await update.message.photo[-1].get_file()
        image_data = await photo_file.download_as_bytearray()

        logger.info(f"📸 Photo received, size: {len(image_data)} bytes")

        # === ВЫЗОВ VISION API (без настроения) ===
        logger.info("🖼️ Sending request to Vision API...")
        response = await analyze_image(
            image_data=bytes(image_data),
            user_message=user_message,
            mood_description="happy"
        )
        logger.info(f"🖼️ Vision API response: {response[:100] if response else 'None'}")

        if not response:
            response = "🖼️ Oh, what a beautiful picture! My eyes are dazzled by such magnificence! 😄"

        await status_message.delete()

        if update.message.chat.type == "private":
            await update.message.reply_text(f"🖼️ {response}")
        else:
            await update.message.reply_text(
                f"🖼️ {response}",
                reply_to_message_id=update.message.message_id
            )

        context_manager.save_context(user_id, f"[Photo] {user_message}", response)
        logger.info("✅ Photo processed successfully")

    except Exception as e:
        logger.error(f"❌ Error processing photo: {e}")
        await status_message.edit_text(
            "🖼️ Oh, what a beautiful picture! "
            "I'm a little blind from such magnificence! 😄"
        )
