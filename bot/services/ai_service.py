import logging
import base64
import os
import time
from pathlib import Path
from typing import Optional, List
from openai import AsyncOpenAI
from bot.config import Config
from bot.core.constants import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

async def get_rarity_response(
    user_message: str,
    mood_description: str = "happy",
    context_history: Optional[List[dict]] = None
) -> Optional[str]:
    try:
        client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        system_prompt = SYSTEM_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Your current mood is: {mood_description}"}
        ]

        if context_history:
            messages.extend(context_history[-10:])

        messages.append({"role": "user", "content": user_message})

        response = await client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            max_tokens=Config.OPENAI_MAX_TOKENS,
            temperature=Config.OPENAI_TEMPERATURE,
            timeout=30.0
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        return None

    except Exception as e:
        logger.error(f"❌ OpenAI error: {e}")
        return None

async def generate_image(prompt: str) -> Optional[str]:
    # Временно отключаем генерацию изображений
    logger.info(f"🎨 Генерация изображений временно недоступна. Запрос: {prompt[:50]}...")
    return None

async def analyze_image(image_data: bytes, user_message: Optional[str] = None) -> Optional[str]:
    try:
        client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        base64_image = base64.b64encode(image_data).decode('utf-8')

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": user_message or "Опиши, что ты видишь на этом изображении, и дай совет по стилю или рукоделию."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500,
            temperature=0.8
        )

        return response.choices[0].message.content.strip() if response.choices else None
    except Exception as e:
        logger.error(f"❌ Vision error: {e}")
        return None

async def transcribe_audio(audio_data: bytes, file_extension: str = ".ogg") -> Optional[str]:
    try:
        client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        audio_dir = Path(Config.AUDIO_DIR)
        audio_dir.mkdir(parents=True, exist_ok=True)

        audio_path = audio_dir / f"voice_{int(time.time())}{file_extension}"
        with open(audio_path, "wb") as f:
            f.write(audio_data)

        with open(audio_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru"
            )

        os.remove(audio_path)
        return transcription.text.strip() if transcription.text else None
    except Exception as e:
        logger.error(f"❌ Whisper error: {e}")
        return None
