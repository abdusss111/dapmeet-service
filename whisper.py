import aiohttp
import os
from dotenv import load_dotenv
load_dotenv()
async def call_whisper(audio_bytes: bytes) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/audio/transcriptions"

    async with aiohttp.ClientSession() as session:
        form_data = aiohttp.FormData()
        form_data.add_field("file", audio_bytes, filename="audio.webm", content_type="audio/webm")
        form_data.add_field("model", "whisper-1")
        form_data.add_field("language", "ru")

        headers = {"Authorization": f"Bearer {api_key}"}

        async with session.post(url, data=form_data, headers=headers) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(f"OpenAI error {response.status}: {text}")
            return await response.json()
