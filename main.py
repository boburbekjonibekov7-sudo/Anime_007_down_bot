# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import config
from bot_factory import build_dispatcher
from database.db import init_db, check_vip_expiry


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


# ==================== WEB SERVER ====================
async def health_check(request):
    return web.Response(text="Ani Yuki bot is running!")


def create_web_app(bot: Bot, dp: Dispatcher) -> web.Application:
    """Webhook server: "/" health check + "/webhook" Telegram update endpoint"""
    app = web.Application()
    app.router.add_get("/", health_check)

    if config.WEBHOOK_URL:
        handler_kwargs = {}
        if config.WEBHOOK_SECRET:
            handler_kwargs["secret_token"] = config.WEBHOOK_SECRET

        SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            **handler_kwargs
        ).register(app, path=config.WEBHOOK_PATH)

        setup_application(app, dp, bot=bot)

    return app


async def start_web_server():
    """Polling rejimida faqat health check uchun server (Render talabi)"""
    app = web.Application()
    app.router.add_get("/", health_check)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        config.PORT
    )

    await site.start()

    logger.info(f"🌐 Web server started on port {config.PORT}")


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

    if config.WEBHOOK_URL:
        webhook_url = config.WEBHOOK_URL.rstrip("/") + config.WEBHOOK_PATH

        kwargs = {
            "url": webhook_url,
            "allowed_updates": used_updates,
            "drop_pending_updates": True,
        }

        if config.WEBHOOK_SECRET:
            kwargs["secret_token"] = config.WEBHOOK_SECRET

        await bot.set_webhook(**kwargs)

        logger.info(f"✅ Webhook o'rnatildi: {webhook_url}")

    logger.info("🚀 Bot muvaffaqiyatli ishga tushdi!")


# ==================== MAIN ====================
async def main():

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = build_dispatcher()

    global used_updates
    used_updates = dp.resolve_used_update_types()

    dp.startup.register(on_startup)

    logger.info("🚀 Bot ishga tushmoqda...")


    if config.WEBHOOK_URL:
        # ==================== WEBHOOK REJIMI ====================
        app = create_web_app(bot, dp)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", config.PORT)
        await site.start()

        logger.info(f"🌐 Webhook server http://0.0.0.0:{config.PORT}{config.WEBHOOK_PATH} da ishga tushdi")

        try:
            await asyncio.Event().wait()
        finally:
            await runner.cleanup()
            await bot.session.close()

    else:
        # ==================== POLLING REJIMI ====================
        # Render uchun port ochish
        await start_web_server()

        try:
            await dp.start_polling(
                bot,
                allowed_updates=used_updates,
                drop_pending_updates=True
            )

        finally:
            await bot.session.close()

            logger.info("Bot to'xtatildi.")



if __name__ == "__main__":
    asyncio.run(main())