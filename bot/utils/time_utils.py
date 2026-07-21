from datetime import datetime
from bot.config import Config

def is_working_hours() -> bool:
    current_hour = datetime.now().hour
    return Config.WORK_START_HOUR <= current_hour < Config.WORK_END_HOUR

def get_working_status_message() -> str:
    return f"⏰ Бот работает с {Config.WORK_START_HOUR}:00 до {Config.WORK_END_HOUR}:00\nПриходите позже! 💎"
