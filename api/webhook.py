# api/webhook.py
# Vercel serverless funksiya: Telegram webhook uchun ASGI app.
# Vercel'da: / va /webhook yo'llari vercel.json rewrites orqali shu funksiyaga keladi.
import os
import sys

# Repo ildizini sys.path'ga qo'shish (config, database, bot_factory import qilish uchun)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Vercel serverless: fayl tizimi o'qish uchun, faqat /tmp yozish mumkin.
# SQLite ma'lumotlar bazasi /tmp da saqlanadi (cold start'da tozalanadi - cheklov, pastga qarang).
os.environ.setdefault("DB_PATH", "/tmp/anime_bot.db")

from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI, Request, Response

from config import config
from bot_factory import build_dispatcher
from database.db import init_db

bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = build_dispatcher()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Har cold start'da jadvalarni yaratish (idempotent)
    await init_db()
    yield


app = FastAPI(title="Ani Yuki Bot Webhook", lifespan=lifespan)


@app.get("/")
async def health():
    return {"status": "Ani Yuki bot is running!"}


@app.post("/webhook")
async def webhook(request: Request):
    # Ixtiyoriy xavfsizlik: X-Telegram-Bot-Api-Secret-Token tekshiruvi
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    if config.WEBHOOK_SECRET and secret != config.WEBHOOK_SECRET:
        return Response(status_code=401)

    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return {"ok": True}
