import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bot.config import Config
from bot.services.ai_service import get_rarity_response

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()
DB_PATH = Config.DATA_DIR / "subscriptions.db"

def _get_connection():
    return sqlite3.connect(DB_PATH)

def _init_db():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS subscriptions (chat_id INTEGER PRIMARY KEY, subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()

def add_chat(chat_id: int):
    _init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO subscriptions (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()
    logger.info(f"📋 Чат {chat_id} добавлен для рассылки")

def remove_chat(chat_id: int):
    _init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscriptions WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    logger.info(f"📋 Чат {chat_id} удалён из рассылки")

def get_active_chats():
    _init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM subscriptions")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    add_chat(chat_id)
    await update.message.reply_text(
        "💎 *Ты подписалась на ежедневные рассылки Рарити!*\n\n"
        "✨ Каждый день в 9:30 я буду присылать тебе вдохновение,\n"
        "а в 18:00 — полезный совет по рукоделию или стилю!\n\n"
        "Чтобы отписаться, напиши /unsubscribe 💎",
        parse_mode="Markdown"
    )

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    remove_chat(chat_id)
    await update.message.reply_text(
        "😢 *Ты отписалась от рассылок!*\n\n"
        "Если захочешь вернуться — напиши /subscribe 💎",
        parse_mode="Markdown"
    )

async def send_inspiration(app):
    active_chats = get_active_chats()
    if not active_chats:
        return
    logger.info(f"💎 Отправка вдохновения в {len(active_chats)} чатов...")
    response = await get_rarity_response(
        user_message="Дай короткую, вдохновляющую фразу или цитату о красоте, творчестве или гармонии. Говори как Рарити — изящно, с душой.",
        mood_description="happy"
    )
    if not response:
        response = "💎 *Бриллиантовое вдохновение:* Сегодня — идеальный день, чтобы добавить блеска в свою жизнь! ✨"
    for chat_id in active_chats:
        try:
            await app.bot.send_message(chat_id=chat_id, text=response, parse_mode="Markdown")
            logger.info(f"✅ Вдохновение отправлено в чат {chat_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в чат {chat_id}: {e}")
            if "bot was blocked" in str(e) or "chat not found" in str(e):
                remove_chat(chat_id)

async def send_daily_tip(app):
    active_chats = get_active_chats()
    if not active_chats:
        return
    logger.info(f"🧵 Отправка совета дня в {len(active_chats)} чатов...")
    response = await get_rarity_response(
        user_message="Дай короткий, полезный совет по рукоделию, стилю или ремонту одежды. Говори как Рарити.",
        mood_description="happy"
    )
    if not response:
        response = "🧵 *Совет от Рарити:* У тебя есть старая рубашка? Не спеши её выбрасывать! Из рукавов можно сделать модные повязки для волос, а из воротника — оригинальный браслет. Твори! 🎀"
    for chat_id in active_chats:
        try:
            await app.bot.send_message(chat_id=chat_id, text=response, parse_mode="Markdown")
            logger.info(f"✅ Совет дня отправлен в чат {chat_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в чат {chat_id}: {e}")
            if "bot was blocked" in str(e) or "chat not found" in str(e):
                remove_chat(chat_id)

def start_scheduler(app):
    try:
        _init_db()
        scheduler.add_job(send_inspiration, CronTrigger(hour=9, minute=30), args=[app], id='rarity_inspiration', replace_existing=True)
        scheduler.add_job(send_daily_tip, CronTrigger(hour=18, minute=0), args=[app], id='rarity_tip', replace_existing=True)
        scheduler.start()
        logger.info("✅ Планировщик Рарити запущен: вдохновение в 9:30, совет дня в 18:00")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске планировщика: {e}")
