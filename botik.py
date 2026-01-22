print("Bot loaded")

import asyncio
import time
import requests
import urllib.parse
from collections import defaultdict

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# ================== CONFIG ==================

BOT_TOKEN = ""

BASE_URL = "https://text.pollinations.ai/"
TEMP = "0.7"

PROMPT_PARTS = [
    "sarcastic",
    "butler",
    "remember",
    "dialog",
    "reply",
    "russian"
]

# ================== BOT ==================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================== MEMORY ==================

memory = defaultdict(list)
MAX_HISTORY = 5

# ================== RATE LIMIT ==================

last_request_time = {}
COOLDOWN_SECONDS = 3

# ================== AI FUNCTION ==================

def ai_generate(user_id, text):
    if not text.strip():
        return "Вы решили помолчать. Смело."

    now = time.time()
    last = last_request_time.get(user_id, 0)

    if now - last < COOLDOWN_SECONDS:
        return "Не так быстро. Я всё-таки дворецкий, а не сервер."

    last_request_time[user_id] = now

    memory[user_id].append("User:" + text)
    memory[user_id] = memory[user_id][-MAX_HISTORY:]

    prompt = " ".join(PROMPT_PARTS)
    context = " | ".join(memory[user_id])
    full_prompt = prompt + " " + context

    encoded = urllib.parse.quote(full_prompt, safe="")
    url = BASE_URL + encoded + "?temperature=" + TEMP

    try:
        r = requests.get(url, timeout=20)

        if r.status_code == 429:
            return "Слишком много вопросов подряд. Умерьте пыл."

        if r.status_code != 200:
            return "Сегодня я не в настроении отвечать."

        answer = r.text.strip()

        memory[user_id].append("Bot:" + answer)
        memory[user_id] = memory[user_id][-MAX_HISTORY:]

        return answer

    except:
        return "Произошло нечто неприятное и совершенно неожиданное."

# ================== HANDLERS ==================

@dp.message(CommandStart())
async def start(message: types.Message):
    memory[message.from_user.id].clear()
    await message.answer("Я здесь. Можем поговорить.")

@dp.message()
async def chat(message: types.Message):
    reply = ai_generate(message.from_user.id, message.text)
    await message.answer(reply)

# ================== RUN ==================

async def main():
    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
