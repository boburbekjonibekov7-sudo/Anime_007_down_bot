# admin/guide.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import get_all_animes, is_admin
from keyboards.admin_kb import admin_guide_kb, back_admin_kb
from aiogram.utils.keyboard import InlineKeyboardBuilder
from filters.admin_filter import IsAdminFilter

router = Router()

# ==================== QO'LLANMA ====================
@router.message(F.text == "📖 Qo'llanma", IsAdminFilter())
async def cmd_admin_guide(message: Message):
    if not await is_admin(message.from_user.id):
        return
    await message.answer(
        "📖 Admin panel qo'llanmasi\n\nQaysi turni ko'rmoqchisiz?",
        reply_markup=admin_guide_kb()
    )

@router.callback_query(F.data == "guide_short")
async def cb_guide_short(call: CallbackQuery):
    text = (
        "📖 *QISQA QO'LLANMA*\n\n"
        "📡 *Kanal boshqaruvi* — Majburiy obuna kanallarni qo'shish/o'chirish\n\n"
        "🎬 *Anime yuklash* — Yangi anime qo'shish, qismlar yuklash\n\n"
        "📋 *Kodlar paneli* — Anime tahrirlash, qism qo'shish/o'chirish\n\n"
        "📋 *Kodlar ro'yxati* — Barcha animeler ro'yxati\n\n"
        "📤 *Post qilish* — Animeni kanalga post qilish\n\n"
        "✉️ *Xabar yuborish* — Foydalanuvchilarga xabar yuborish\n\n"
        "👥 *Adminlar* — Admin qo'shish/o'chirish\n\n"
        "🤖 *Bot paneli* — Bot sozlamalari, VIP, baza va boshqalar\n\n"
        "👤 *Foydalanuvchi boshqarish* — User ma'lumotlari va boshqaruv\n\n"
        "📊 *Statistika* — To'liq bot statistikasi"
    )
    b = InlineKeyboardBuilder()
    b.button(text="📚 To'liq qo'llanma", callback_data="guide_full")
    b.button(text="🔙 Orqaga", callback_data="admin_cancel")
    b.adjust(1)
    await call.message.edit_text(text, reply_markup=b.as_markup(), parse_mode="Markdown")

@router.callback_query(F.data == "guide_full")
async def cb_guide_full(call: CallbackQuery):
    text = (
        "📚 *TO'LIQ QO'LLANMA*\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "📡 *1. KANAL BOSHQARUVI*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "➕ Kanal qo'shish:\n"
        "  • Ommaviy/Shaxsiy — ID, havola yoki post orqali\n"
        "  • So'rovli havola — invite link orqali\n"
        "  • Oddiy havola — Instagram, sayt havolasi\n"
        "📋 Ro'yxat — mavjud kanallarni ko'rish\n"
        "🗑 O'chirish — kanallarni ro'yxatdan olib tashlash\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "🎬 *2. ANIME YUKLASH*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "1. Kod kiriting (masalan: 574)\n"
        "2. Anime nomini kiriting\n"
        "3. Janrni kiriting yoki /skip\n"
        "4. Studiyani kiriting yoki /skip\n"
        "5. Posterni yuboring (rasm/video)\n"
        "6. Qismlarni ketma-ket yuboring\n"
        "7. /done yozing — saqlandi!\n"
        "Auto post yoqiq bo'lsa — kanalga avtomatik ketadi.\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "📋 *3. KODLAR PANELI (TAHRIRLASH)*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Kodni kiriting → amallarni tanlang:\n"
        "  ✏️ Postni tahrirlash — nom, janr, poster\n"
        "  🔢 Kodni tahrirlash — yangi kod\n"
        "  ➕ Qism qo'shish — yangi video yuborish\n"
        "  ➕ Fasl qo'shish — yangi fasl\n"
        "  🗑 Qismni o'chirish — raqamini tanlash\n"
        "  🔄 Qismni almashtirish — yangi video\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "📤 *4. POST QILISH*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "1. Anime kodini kiriting\n"
        "2. Kanallarni tanlang (multi-select)\n"
        "3. 'Jo'natish' tugmasini bosing\n"
        "Har kanal o'z nomi bilan alohida post oladi!\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "💎 *5. VIP BOSHQARUVI*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "  ➕ VIP berish — ID va kun miqdori\n"
        "  ❌ VIP olish — ID kiritish\n"
        "  💳 Karta boshqaruvi — karta qo'shish/o'chirish\n"
        "  💰 Narxlar — 1 hafta, 2 hafta, 1 oy\n"
        "  🧾 To'lov so'rovlari — tasdiqlash/rad etish\n"
        "  🎟 Promokod — 6 xonali kod yaratish\n"
        "  💎 Anime VIP — qism yoki fasldan VIP qilish\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "⚙️ *6. SOZLAMALAR*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "  📢 Auto post — anime yuklaganda avtomatik post\n"
        "  🔢 Auto kod — avtomatik kod generatsiya\n"
        "  🔗 Ulashish — animelarni ulashish\n"
        "  ✏️ Tugma nomlari — asosiy menyu tugmalarini o'zgartirish\n"
        "  📝 Kirish matni — /start xabarini o'zgartirish\n"
        "  🖼 Kirish media — /start rasmi/videosi\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "✉️ *7. XABAR YUBORISH*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Kimga:\n"
        "  • Bitta foydalanuvchi — ID kiriting\n"
        "  • Barcha — barcha active userlarga\n"
        "  • VIP — faqat VIP userlarga\n"
        "  • Oddiy — faqat oddiy userlarga\n"
        "Usullar:\n"
        "  ✍️ Matn — HTML formatlash qo'llab-quvvatlanadi\n"
        "  🔗 Kod orqali — anime kodi kiritish\n"
        "  📎 Link orqali — kanal post linkini forward qilish\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "🗄 *8. BAZA BOSHQARUVI*\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "  📥 Baza olish — full/userlar/animelar JSON\n"
        "  📤 Baza yuklash — JSON fayldan import\n"
        "  👥 User qo'shish — ID ro'yxati (max 2500)\n"
    )

    b = InlineKeyboardBuilder()
    b.button(text="📖 Qisqa ko'rinish", callback_data="guide_short")
    b.button(text="🔙 Orqaga", callback_data="admin_cancel")
    b.adjust(1)
    await call.message.edit_text(text, reply_markup=b.as_markup(), parse_mode="Markdown")

# ==================== KODLAR RO'YXATI ====================
@router.message(F.text == "📋 Kodlar ro'yxati", IsAdminFilter())
async def cmd_codes_list(message: Message):
    if not await is_admin(message.from_user.id):
        return
    await show_codes_list(message, page=1)

async def show_codes_list(message, page=1, edit=False):
    from database.db import get_setting, get_episodes
    result = await get_all_animes(page=page, per_page=10)
    if not result["items"]:
        text = "📋 Kodlar ro'yxati bo'sh."
        b = InlineKeyboardBuilder()
        b.button(text="🔙 Admin paneli", callback_data="admin_panel")
        if edit:
            await message.edit_text(text, reply_markup=b.as_markup())
        else:
            await message.answer(text, reply_markup=b.as_markup())
        return

    bot_username = await get_setting("bot_username") or "anime_bot"
    text = f"📋 Kodlar ro'yxati ({result['total']} ta) — {page}/{result['pages']} sahifa:\n\n"
    
    b = InlineKeyboardBuilder()
    from aiogram.types import InlineKeyboardButton
    
    for a in result["items"]:
        eps = await get_episodes(a["code"])
        vip_mark = "💎" if a.get("is_vip") else "🔴"
        text += f"{vip_mark} [{a['code']}] {a['name']} — {len(eps)} qism\n"
        b.row(
            InlineKeyboardButton(
                text=f"🔗 {a['name']}",
                url=f"https://t.me/{bot_username}?start={a['code']}"
            ),
            InlineKeyboardButton(
                text="✏️",
                callback_data=f"edit_anime_quick:{a['code']}"
            )
        )

    nav = []
    if page > 1:
        nav.append({"text": "◀️", "cb": f"codes_page:{page-1}"})
    nav.append({"text": f"{page}/{result['pages']}", "cb": "noop"})
    if page < result["pages"]:
        nav.append({"text": "▶️", "cb": f"codes_page:{page+1}"})

    nav_btns = [InlineKeyboardButton(text=n["text"], callback_data=n["cb"]) for n in nav]
    if nav_btns:
        b.row(*nav_btns)
    b.row(InlineKeyboardButton(text="🔙 Admin paneli", callback_data="admin_panel"))

    if edit:
        await message.edit_text(text, reply_markup=b.as_markup())
    else:
        await message.answer(text, reply_markup=b.as_markup())

@router.callback_query(F.data.startswith("edit_anime_quick:"))
async def cb_edit_anime_quick(call: CallbackQuery, state: FSMContext):
    code = int(call.data.split(":")[1])
    from database.db import get_anime, get_episodes, get_seasons
    anime = await get_anime(code)
    if not anime:
        await call.answer("❌ Topilmadi!", show_alert=True)
        return
    eps = await get_episodes(code)
    seasons = await get_seasons(code)
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    b = InlineKeyboardBuilder()
    b.button(text="✏️ Postni tahrirlash", callback_data=f"edit_post:{code}")
    b.button(text="🔢 Kodni tahrirlash", callback_data=f"edit_code_change:{code}")
    b.button(text="➕ Qism qo'shish", callback_data=f"edit_add_ep:{code}")
    b.button(text="➕ Fasl qo'shish", callback_data=f"edit_add_season:{code}")
    b.button(text="🗑 Qismni o'chirish", callback_data=f"edit_del_ep:{code}")
    b.button(text="🔄 Qismni almashtirish", callback_data=f"edit_replace_ep:{code}")
    b.button(text="🔙 Kodlar ro'yxati", callback_data="codes_page:1")
    b.adjust(1)
    await call.message.edit_text(
        f"📋 {anime['name']}\n"
        f"🔢 Kod: {code}\n"
        f"📦 Qismlar: {len(eps)} ta | 📺 Fasllar: {len(seasons)} ta\n\n"
        f"Qaysi amalni bajarmoqchisiz?",
        reply_markup=b.as_markup(),
        parse_mode=None
    )

@router.callback_query(F.data.startswith("codes_page:"))
async def cb_codes_page(call: CallbackQuery):
    page = int(call.data.split(":")[1])
    await show_codes_list(call.message, page=page, edit=True)
