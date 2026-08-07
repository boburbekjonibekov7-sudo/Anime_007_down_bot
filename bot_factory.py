# bot_factory.py
# Dispatcher yig'ish - main.py (Docker/polling) va api/webhook.py (Vercel) ikkalasi ham shu yerdan oladi.
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from middlewares.middlewares import ThrottlingMiddleware, UserMiddleware, VipCheckMiddleware

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


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    # ==================== MIDDLEWARES ====================
    dp.message.middleware(ThrottlingMiddleware(rate_limit=config.RATE_LIMIT))
    dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    dp.message.middleware(VipCheckMiddleware())

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

    return dp
