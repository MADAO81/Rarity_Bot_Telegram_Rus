import logging
import base64
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from bot.config import Config
from bot.core.constants import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def get_rarity_response(
    user_message: str,
    mood_description: str = "happy",
    context_history: Optional[List[Dict]] = None
) -> Optional[str]:
    """Generates a response from Rarity using DeepSeek."""
    try:
        client = AsyncOpenAI(
            api_key=Config.PROXY_API_KEY,
            base_url="https://api.proxyapi.ru/openrouter/v1"
        )

        system_prompt = SYSTEM_PROMPT
        if mood_description == "sad":
            system_prompt += "\n\n⚠️ IMPORTANT: You are in a sad mood right now."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Your current mood is: {mood_description}"}
        ]

        if context_history:
            messages.extend(context_history[-10:])

        messages.append({"role": "user", "content": user_message})

        logger.info(f"🧠 Request to DeepSeek (model: {Config.DEEPSEEK_MODEL})...")

        response = await client.chat.completions.create(
            model=Config.DEEPSEEK_MODEL,
            messages=messages,
            max_tokens=Config.DEEPSEEK_MAX_TOKENS,
            temperature=Config.DEEPSEEK_TEMPERATURE,
            timeout=30.0
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            logger.warning("⚠️ DeepSeek returned empty response")
            return None

    except Exception as e:
        logger.error(f"❌ Error calling DeepSeek: {e}")
        return None


# === ФУНКЦИЯ АНАЛИЗА КАРТИНОК (с русским языком) ===
async def analyze_image(
    image_data: bytes,
    user_message: Optional[str] = None,
    mood_description: str = "happy"
) -> Optional[str]:
    """Analyzes an image using OpenAI Vision API (отвечает на русском)."""
    logger.info("🖼️ Request to OpenAI Vision API...")
    try:
        client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

        system_prompt = SYSTEM_PROMPT
        if mood_description == "sad":
            system_prompt += "\n\nYou are in a sad mood, but still trying to be kind."
        
        # ЯВНО указываем русский язык
        system_prompt += "\n\nIMPORTANT: Always respond in Russian language."

        base64_image = base64.b64encode(image_data).decode('utf-8')

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"User sent an image. {user_message if user_message else 'Describe what you see in the image and comment on it in your style.'} Ответь на русском языке."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

        logger.info("🖼️ Sending request to OpenAI Vision API...")

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500,
            temperature=0.8,
            timeout=30.0
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        else:
            logger.warning("⚠️ Vision API returned empty response")
            return None

    except Exception as e:
        logger.error(f"❌ Error analyzing image: {e}")
        return None


async def generate_image(prompt: str) -> Optional[str]:
    """Generates an image using DALL-E."""
    try:
        client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info(f"🎨 Generating image: {prompt[:50]}...")
        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        if response.data:
            return response.data[0].url
        return None
    except Exception as e:
        logger.error(f"❌ DALL-E error: {e}")
        return None


async def transcribe_audio(
    audio_data: bytes,
    file_extension: str = ".ogg"
) -> Optional[str]:
    """Transcribes audio using OpenAI Whisper."""
    try:
        client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

        audio_dir = Path(Config.AUDIO_DIR)
        audio_dir.mkdir(parents=True, exist_ok=True)

        audio_path = audio_dir / f"voice_{int(time.time())}{file_extension}"
        with open(audio_path, "wb") as f:
            f.write(audio_data)

        logger.info(f"🎤 Sending audio to Whisper...")

        with open(audio_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ru"
            )

        try:
            os.remove(audio_path)
        except:
            pass

        if transcription and transcription.text:
            logger.info(f"✅ Transcription successful: {transcription.text[:50]}...")
            return transcription.text.strip()
        else:
            logger.warning("⚠️ Whisper returned empty response")
            return None

    except Exception as e:
        logger.error(f"❌ Error transcribing audio: {e}")
        return None
