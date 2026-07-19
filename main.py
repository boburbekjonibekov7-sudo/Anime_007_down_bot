# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ==================== RENDER WEB SERVER ====================
async def health_check(request):
    return web.Response(text="Ani Yuki bot is running!")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)

    runner = web.AppRunner(app)
    await runner.setup()

    port = 10000

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    logger.info(f"🌐 Web server started on port {port}")


# ==================== VIP CHECKER ====================
async def vip_checker():
    """Har 30 daqiqada VIP muddati tugagan userlarni tekshirish"""
    while True:
        await asyncio.sleep(1800)

        try:
            await check_vip_expiry()
            logger.info("VIP expiry check completed")

        except Exception as e:
            logger.error(f"VIP checker xatolik: {e}")


# ==================== STARTUP ====================
async def on_startup(bot: Bot):
    await init_db()

    logger.info("✅ Database initialized")

    await check_vip_expiry()

    logger.info("✅ VIP expiry checked on startup")

    asyncio.create_task(vip_checker())

    logger.info("✅ VIP checker task started")

    logger.info("🚀 Bot muvaffaqiyatli ishga tushdi!")


# ==================== MAIN ====================
async def main():

    # Render uchun port ochish
    await start_web_server()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)


    # ==================== MIDDLEWARES ====================

    dp.message.middleware(
        ThrottlingMiddleware(rate_limit=config.RATE_LIMIT)
    )

    dp.callback_query.middleware(
        ThrottlingMiddleware(rate_limit=0.3)
    )

    dp.message.middleware(
        UserMiddleware()
    )

    dp.callback_query.middleware(
        UserMiddleware()
    )

    dp.message.middleware(
        VipCheckMiddleware()
    )


    # ==================== ROUTERS ====================

    dp.include_router(admin_panel_router)
    dp.include_router(channels_router)
    dp.include_router(anime_upload_router)
    dp.include_router(anime_edit_router)
    dp.include_router(broadcast_router)
    dp.include_router(bot_panel_router)
    dp.include_router(guide_router)

    dp.include_router(start_router)
    dp.include_router(anime_router)
    dp.include_router(vip_router)


    dp.startup.register(on_startup)


    logger.info("🚀 Bot ishga tushmoqda...")


    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True
        )

    finally:
        await bot.session.close()

        logger.info("Bot to'xtatildi.")



if __name__ == "__main__":
    asyncio.run(main())