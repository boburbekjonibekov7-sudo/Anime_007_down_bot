# main.py - Vercel Serverless Webhook Handler
import os
import logging
from fastapi import FastAPI, Request, Response
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

from config import config
from database.db import init_db, check_vip_expiry
from middlewares.middlewares import ThrottlingMiddleware, UserMiddleware, VipCheckMiddleware

# ==================== ROUTERS ====================
from admin.panel import router as admin_panel_router
from admin.channels import router as channels_router
from admin.anime_upload import router as anime_upload_router
from admin.anime_edit import router as anime_edit_router
from admin.broadcast import router as broadcast_router
from admin.bot_panel import router as bot_panel_router
from admin.guide import router as guide_router
from user.start import router as start_router
from user.anime import router as anime_router
from user.vip import router as vip_router


# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ==================== FASTAPI APP ====================
app = FastAPI()

# Global bot and dispatcher instances
_bot: Bot = None
_dp: Dispatcher = None
_initialized = False


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML
            )
        )
    return _bot


def get_dispatcher() -> Dispatcher:
    global _dp, _initialized
    
    if _dp is None:
        storage = MemoryStorage()
        _dp = Dispatcher(storage=storage)
        
        # ==================== MIDDLEWARES ====================
        _dp.message.middleware(
            ThrottlingMiddleware(rate_limit=config.RATE_LIMIT)
        )
        _dp.callback_query.middleware(
            ThrottlingMiddleware(rate_limit=0.3)
        )
        _dp.message.middleware(UserMiddleware())
        _dp.callback_query.middleware(UserMiddleware())
        _dp.message.middleware(VipCheckMiddleware())
        
        # ==================== ROUTERS ====================
        _dp.include_router(admin_panel_router)
        _dp.include_router(channels_router)
        _dp.include_router(anime_upload_router)
        _dp.include_router(anime_edit_router)
        _dp.include_router(broadcast_router)
        _dp.include_router(bot_panel_router)
        _dp.include_router(guide_router)
        _dp.include_router(start_router)
        _dp.include_router(anime_router)
        _dp.include_router(vip_router)
        
        _initialized = True
        logger.info("✅ Dispatcher initialized with routers and middlewares")
    
    return _dp


async def initialize_database():
    """Initialize database on first request if needed"""
    global _initialized
    if not _initialized:
        await init_db()
        await check_vip_expiry()
        logger.info("✅ Database initialized")
        _initialized = True


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Ani Yuki bot is running!"}


@app.post("/webhook")
async def webhook_handler(request: Request) -> Response:
    """Handle Telegram webhook updates"""
    try:
        # Initialize database on first request
        await initialize_database()
        
        # Get update from request
        body = await request.body()
        update = Update.model_load_json(body.decode())
        
        # Get bot and dispatcher
        bot = get_bot()
        dp = get_dispatcher()
        
        # Process update
        await dp.feed_update(bot, update)
        
        return Response(status_code=200)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status_code=500)


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    global _bot
    if _bot:
        await _bot.session.close()
        logger.info("Bot session closed")