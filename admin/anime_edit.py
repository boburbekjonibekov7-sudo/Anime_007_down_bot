# admin/anime_edit.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.db import (
    get_anime, update_anime, delete_episode, add_episode,
    get_episodes, get_seasons, add_season, is_admin,
    update_episode_vip, clear_episode_vip, get_episode
)
from keyboards.admin_kb import (
    cancel_admin_kb, back_admin_kb, back_cancel_admin_kb, vip_anime_kb
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import logging
from filters.admin_filter import IsAdminFilter

logger = logging.getLogger(__name__)
router = Router()

class AnimeEditStates(StatesGroup):
    waiting_code = State()
    waiting_new_code = State()
    waiting_new_name = State()
    waiting_new_genre = State()
    waiting_new_poster = State()
    waiting_ep_add = State()
    waiting_ep_del_num = State()
    waiting_ep_replace_num = State()
    waiting_ep_replace_file = State()
    waiting_season_name = State()
    waiting_vip_ep_num = State()
    waiting_vip_season_num = State()
    waiting_vip_anime_select = State()
    # Anime statusi
    waiting_status_code = State()
    # Video/Rasm
    waiting_media_code = State()
    waiting_media_ep = State()
    waiting_media_file = State()

# ==================== KODLAR PANELI (TAHRIRLASH) ====================
@router.message(F.text == "📋 Kodlar paneli", IsAdminFilter())
async def cmd_codes_panel(message: Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await state.clear()
    await state.set_state(AnimeEditStates.waiting_code)
    await state.update_data(action="main")
    await message.answer(
        "📋 Tahrirlamoqchi bo'lgan anime kodini kiriting:",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_code)
async def process_edit_code(message: Message, state: FSMContext):
    try:
        code = int(message.text.strip())
    except:
        await message.answer("❌ Faqat raqam kiriting!", reply_markup=cancel_admin_kb())
        return

    anime = await get_anime(code)
    if not anime:
        await message.answer(f"❌ {code} kodli anime topilmadi!", reply_markup=cancel_admin_kb())
        return

    episodes = await get_episodes(code)
    seasons = await get_seasons(code)
    await state.update_data(edit_code=code)
    await state.clear()

    b = InlineKeyboardBuilder()
    b.button(text="✏️ Postni tahrirlash", callback_data=f"edit_post:{code}")
    b.button(text="🔢 Kodni tahrirlash", callback_data=f"edit_code_change:{code}")
    b.button(text="➕ Qism qo'shish", callback_data=f"edit_add_ep:{code}")
    b.button(text="➕ Fasl qo'shish", callback_data=f"edit_add_season:{code}")
    b.button(text="🗑 Qismni o'chirish", callback_data=f"edit_del_ep:{code}")
    b.button(text="🔄 Qismni almashtirish", callback_data=f"edit_replace_ep:{code}")
    b.button(text="🔙 Admin paneli", callback_data="admin_panel")
    b.adjust(1)

    ep_count = len(episodes)
    season_count = len(seasons)
    await message.answer(
        f"📋 {anime['name']}\n"
        f"🔢 Kod: {code}\n"
        f"📦 Qismlar: {ep_count} ta\n"
        f"📺 Fasllar: {season_count} ta\n\n"
        f"Qaysi amalni bajarmoqchisiz?",
        reply_markup=b.as_markup(),
        parse_mode=None
    )

# ==================== POST TAHRIRLASH ====================
@router.callback_query(F.data.startswith("edit_post:"))
async def cb_edit_post(call: CallbackQuery, state: FSMContext):
    code = int(call.data.split(":")[1])
    await state.update_data(edit_code=code, edit_field="name")
    await state.set_state(AnimeEditStates.waiting_new_name)
    await call.message.edit_text(
        "✏️ Yangi anime nomini kiriting:\n\n/skip — o'zgartimaslik",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_new_name)
async def process_new_name(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["edit_code"]
    if message.text.strip() != "/skip":
        await update_anime(code, name=message.text.strip())
    await state.set_state(AnimeEditStates.waiting_new_genre)
    await message.answer(
        "✏️ Yangi janrni kiriting:\n\n/skip — o'zgartimaslik",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_new_genre)
async def process_new_genre(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["edit_code"]
    if message.text.strip() != "/skip":
        await update_anime(code, genre=message.text.strip())
    await state.set_state(AnimeEditStates.waiting_new_poster)
    await message.answer(
        "🖼 Yangi posterni yuboring (rasm/video):\n\n/skip — o'zgartimaslik",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_new_poster)
async def process_new_poster(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["edit_code"]
    if message.text and message.text.strip() == "/skip":
        pass
    elif message.photo:
        await update_anime(code, poster_file_id=message.photo[-1].file_id)
    elif message.video:
        await update_anime(code, poster_file_id=message.video.file_id)
    await state.clear()
    anime = await get_anime(code)
    await message.answer(
        f"✅ {anime['name']} ma'lumotlari yangilandi!",
        reply_markup=back_admin_kb(),
        parse_mode=None
    )

# ==================== KOD TAHRIRLASH ====================
@router.callback_query(F.data.startswith("edit_code_change:"))
async def cb_edit_code(call: CallbackQuery, state: FSMContext):
    code = int(call.data.split(":")[1])
    await state.update_data(edit_code=code)
    await state.set_state(AnimeEditStates.waiting_new_code)
    await call.message.edit_text(
        f"🔢 Yangi kodni kiriting:\n(Joriy kod: {code})",
        reply_markup=cancel_admin_kb(),
        parse_mode=None
    )

@router.message(AnimeEditStates.waiting_new_code)
async def process_new_code(message: Message, state: FSMContext):
    data = await state.get_data()
    old_code = data["edit_code"]
    try:
        new_code = int(message.text.strip())
    except:
        await message.answer("❌ Faqat raqam!", reply_markup=cancel_admin_kb())
        return
    existing = await get_anime(new_code)
    if existing:
        await message.answer(f"❌ {new_code} kod allaqachon mavjud!", reply_markup=cancel_admin_kb())
        return
    await update_anime(old_code, new_code=new_code)
    await state.clear()
    await message.answer(
        f"✅ Kod yangilandi: {old_code} → {new_code}",
        reply_markup=back_admin_kb(),
        parse_mode=None
    )

# ==================== QISM QO'SHISH ====================
@router.callback_query(F.data.startswith("edit_add_ep:"))
async def cb_add_ep(call: CallbackQuery, state: FSMContext):
    code = int(call.data.split(":")[1])
    seasons = await get_seasons(code)

    if len(seasons) > 1:
        b = InlineKeyboardBuilder()
        for s in seasons:
            b.button(text=f"📺 {s['season_number']}-fasl", callback_data=f"add_ep_season:{code}:{s['season_number']}")
        b.button(text="❌ Bekor qilish", callback_data="admin_cancel")
        b.adjust(1)
        await call.message.edit_text(
            "📺 Qaysi faslga qism qo'shmoqchisiz?",
            reply_markup=b.as_markup()
        )
    else:
        await state.update_data(edit_code=code, edit_season=1)
        await state.set_state(AnimeEditStates.waiting_ep_add)
        await call.message.edit_text(
            "📤 Qo'shmoqchi bo'lgan qismni yuboring (video):\n\nTugatgach: /done",
            reply_markup=cancel_admin_kb()
        )

@router.callback_query(F.data.startswith("add_ep_season:"))
async def cb_add_ep_season(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    code = int(parts[1])
    season = int(parts[2])
    await state.update_data(edit_code=code, edit_season=season)
    await state.set_state(AnimeEditStates.waiting_ep_add)
    await call.message.edit_text(
        f"📤 {season}-faslga qism yuboring (video):\n\nTugatgach: /done",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_ep_add, F.content_type == ContentType.VIDEO)
async def process_add_ep(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["edit_code"]
    season = data.get("edit_season", 1)
    eps = await get_episodes(code, season)
    ep_num = len(eps) + 1
    await add_episode(code, season, ep_num, message.video.file_id)
    await message.answer(
        f"✅ {ep_num}-qism qo'shildi.\nDavom eting yoki /done yozing."
    )

@router.message(AnimeEditStates.waiting_ep_add, F.text == "/done")
async def process_add_ep_done(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["edit_code"]
    await state.clear()
    eps = await get_episodes(code)
    await message.answer(
        f"✅ Qismlar qo'shildi! Jami: {len(eps)} ta",
        reply_markup=back_admin_kb()
    )

# ==================== FASL QO'SHISH ====================
@router.callback_query(F.data.startswith("edit_add_season:"))
async def cb_add_season(call: CallbackQuery, state: FSMContext):
    code = int(call.data.split(":")[1])
    seasons = await get_seasons(code)
    new_season_num = len(seasons) + 1
    await state.update_data(edit_code=code, new_season_num=new_season_num)
    await state.set_state(AnimeEditStates.waiting_season_name)
    await call.message.edit_text(
        f"📺 {new_season_num}-fasl nomi kiriting:\n\n/skip — avtomatik nom",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_season_name)
async def process_season_name(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["edit_code"]
    season_num = data["new_season_num"]
    name = None if message.text.strip() == "/skip" else message.text.strip()
    await add_season(code, season_num, name)
    await state.clear()
    await message.answer(
        f"✅ {season_num}-fasl qo'shildi!",
        reply_markup=back_admin_kb()
    )

# ==================== QISMNI O'CHIRISH ====================
@router.callback_query(F.data.startswith("edit_del_ep:"))
async def cb_del_ep(call: CallbackQuery, state: FSMContext):
    code = int(call.data.split(":")[1])
    eps = await get_episodes(code)
    await state.update_data(edit_code=code)
    await state.set_state(AnimeEditStates.waiting_ep_del_num)

    b = InlineKeyboardBuilder()
    for ep in eps:
        b.button(text=str(ep["episode_number"]), callback_data=f"del_ep_do:{code}:{ep['season_number']}:{ep['episode_number']}")
    b.button(text="❌ Bekor qilish", callback_data="admin_cancel")
    b.adjust(5)
    await call.message.edit_text(
        f"🗑 O'chirish uchun qism raqamini tanlang:",
        reply_markup=b.as_markup()
    )

@router.callback_query(F.data.startswith("del_ep_do:"))
async def cb_del_ep_do(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    code = int(parts[1])
    season = int(parts[2])
    ep_num = int(parts[3])
    await delete_episode(code, season, ep_num)
    await state.clear()
    await call.message.edit_text(
        f"✅ {ep_num}-qism o'chirildi!",
        reply_markup=back_admin_kb()
    )

# ==================== QISMNI ALMASHTIRISH ====================
@router.callback_query(F.data.startswith("edit_replace_ep:"))
async def cb_replace_ep(call: CallbackQuery, state: FSMContext):
    code = int(call.data.split(":")[1])
    eps = await get_episodes(code)
    await state.update_data(edit_code=code)

    b = InlineKeyboardBuilder()
    for ep in eps:
        b.button(text=str(ep["episode_number"]), callback_data=f"replace_ep_sel:{code}:{ep['season_number']}:{ep['episode_number']}")
    b.button(text="❌ Bekor qilish", callback_data="admin_cancel")
    b.adjust(5)
    await call.message.edit_text(
        "🔄 Qaysi qismni almashtirasiz?",
        reply_markup=b.as_markup()
    )

@router.callback_query(F.data.startswith("replace_ep_sel:"))
async def cb_replace_ep_sel(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    code = int(parts[1])
    season = int(parts[2])
    ep_num = int(parts[3])
    await state.update_data(edit_code=code, replace_season=season, replace_ep=ep_num)
    await state.set_state(AnimeEditStates.waiting_ep_replace_file)
    await call.message.edit_text(
        f"📤 {ep_num}-qism uchun yangi videoni yuboring:",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_ep_replace_file, F.content_type == ContentType.VIDEO)
async def process_replace_ep(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["edit_code"]
    season = data["replace_season"]
    ep_num = data["replace_ep"]
    await delete_episode(code, season, ep_num)
    await add_episode(code, season, ep_num, message.video.file_id)
    await state.clear()
    await message.answer(
        f"✅ {ep_num}-qism almashtirildi!",
        reply_markup=back_admin_kb()
    )

# ==================== ANIME STATUSI ====================
@router.callback_query(F.data == "bp_anime_status")
async def cb_anime_status(call: CallbackQuery, state: FSMContext):
    await state.set_state(AnimeEditStates.waiting_status_code)
    await call.message.edit_text(
        "🎬 ANIME FORWARD STATUSINI BOSHQARISH\n\n📝 Anime kodini kiriting:",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_status_code)
async def process_status_code(message: Message, state: FSMContext):
    try:
        code = int(message.text.strip())
    except:
        await message.answer("❌ Faqat raqam!", reply_markup=cancel_admin_kb())
        return
    anime = await get_anime(code)
    if not anime:
        await message.answer("❌ Anime topilmadi!", reply_markup=cancel_admin_kb())
        return
    await state.clear()
    status = "✅ ON" if anime.get("forward_status", 1) else "❌ OFF"
    b = InlineKeyboardBuilder()
    b.button(text="✅ ON qilish", callback_data=f"forward_on:{code}")
    b.button(text="❌ OFF qilish", callback_data=f"forward_off:{code}")
    b.button(text="❌ Bekor qilish", callback_data="admin_cancel")
    b.adjust(2, 1)
    await message.answer(
        f"🎬 Anime: {anime['name']}\n"
        f"Status: {status}\n\n"
        f"Forward statusini o'zgartiring:",
        reply_markup=b.as_markup(),
        parse_mode=None
    )

@router.callback_query(F.data.startswith("forward_on:"))
async def cb_forward_on(call: CallbackQuery):
    code = int(call.data.split(":")[1])
    await update_anime(code, forward_status=1)
    await call.message.edit_text(
        f"✅ Kod {code} — Forward: ON qilindi!",
        reply_markup=back_admin_kb("bot_panel")
    )

@router.callback_query(F.data.startswith("forward_off:"))
async def cb_forward_off(call: CallbackQuery):
    code = int(call.data.split(":")[1])
    await update_anime(code, forward_status=0)
    await call.message.edit_text(
        f"✅ Kod {code} — Forward: OFF qilindi!",
        reply_markup=back_admin_kb("bot_panel")
    )

# ==================== VIDEO VA RASM ====================
@router.callback_query(F.data == "bp_media")
async def cb_media(call: CallbackQuery, state: FSMContext):
    await state.clear()
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    b = InlineKeyboardBuilder()
    b.button(text="🎬 Animega rasm qo'yish", callback_data="media_add_thumb")
    b.button(text="🔙 Bot paneli", callback_data="bot_panel")
    b.adjust(1)
    try:
        await call.message.edit_text("🖼 Video va Rasm:", reply_markup=b.as_markup())
    except:
        await call.message.answer("🖼 Video va Rasm:", reply_markup=b.as_markup())

@router.callback_query(F.data == "media_add_thumb")
async def cb_media_add_thumb(call: CallbackQuery, state: FSMContext):
    await state.set_state(AnimeEditStates.waiting_media_code)
    await call.message.edit_text(
        "1️⃣2️⃣3️⃣4️⃣ Anime kodini kiriting:",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_media_code)
async def process_media_code(message: Message, state: FSMContext):
    try:
        code = int(message.text.strip())
    except:
        await message.answer("❌ Faqat raqam!", reply_markup=cancel_admin_kb())
        return
    anime = await get_anime(code)
    if not anime:
        await message.answer("❌ Anime topilmadi!", reply_markup=cancel_admin_kb())
        return
    eps = await get_episodes(code)
    await state.update_data(media_code=code)
    await state.set_state(AnimeEditStates.waiting_media_ep)

    b = InlineKeyboardBuilder()
    row = []
    for ep in eps:
        row.append(InlineKeyboardButton(text=f"{ep['episode_number']}-qism", callback_data=f"media_ep:{code}:{ep['season_number']}:{ep['episode_number']}"))
        if len(row) == 3:
            b.row(*row)
            row = []
    if row:
        b.row(*row)
    b.row(InlineKeyboardButton(text="📦 Barchasiga", callback_data=f"media_ep:{code}:0:0"))
    b.row(InlineKeyboardButton(text="🔙 Bot paneli", callback_data="bot_panel"))

    await message.answer(
        f"🎬 {anime['name']} — {len(eps)} ta qism\n\nQaysi qismga rasm qo'ymoqchisiz?",
        reply_markup=b.as_markup(),
        parse_mode=None
    )

@router.callback_query(F.data.startswith("media_ep:"))
async def cb_media_ep(call: CallbackQuery, state: FSMContext):
    parts = call.data.split(":")
    code = int(parts[1])
    season = int(parts[2])
    ep_num = int(parts[3])
    await state.update_data(media_code=code, media_season=season, media_ep=ep_num)
    await state.set_state(AnimeEditStates.waiting_media_file)
    await call.message.edit_text(
        "📸 Rasmni yuboring:",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_media_file, F.photo)
async def process_media_file(message: Message, state: FSMContext):
    data = await state.get_data()
    code = data["media_code"]
    season = data.get("media_season", 0)
    ep_num = data.get("media_ep", 0)
    file_id = message.photo[-1].file_id

    from database.db import DB_PATH
    import aiosqlite
    if ep_num == 0:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("UPDATE episodes SET thumbnail_file_id=? WHERE anime_code=?", (file_id, code))
            await db.commit()
        await message.answer("✅ Barcha qismlarga rasm qo'shildi!", reply_markup=back_admin_kb("bot_panel"))
    else:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE episodes SET thumbnail_file_id=? WHERE anime_code=? AND season_number=? AND episode_number=?",
                (file_id, code, season, ep_num)
            )
            await db.commit()
        await message.answer(f"✅ {ep_num}-qismga rasm qo'shildi!", reply_markup=back_admin_kb("bot_panel"))
    await state.clear()

# ==================== VIP ANIME SOZLASH ====================
@router.callback_query(F.data == "vm_vip_anime")
async def cb_vip_anime_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(action="vip_anime")
    await state.set_state(AnimeEditStates.waiting_vip_anime_select)
    await call.message.edit_text(
        "💎 VIP sozlash uchun anime kodini kiriting:",
        reply_markup=cancel_admin_kb()
    )

@router.message(AnimeEditStates.waiting_vip_anime_select)
async def process_vip_anime_select(message: Message, state: FSMContext):
    try:
        code = int(message.text.strip())
    except:
        await message.answer("❌ Faqat raqam kiriting!", reply_markup=cancel_admin_kb())
        return
    anime = await get_anime(code)
    if not anime:
        await message.answer("❌ Anime topilmadi!", reply_markup=cancel_admin_kb())
        return
    await state.update_data(edit_code=code)
    await message.answer(
        f"💎 {anime['name']} — VIP sozlash:\n\nQaysi turda VIP qilasiz?",
        reply_markup=vip_anime_kb(),
        parse_mode=None
    )

@router.callback_query(F.data.startswith("vip_anime:"))
async def cb_vip_anime_action(call: CallbackQuery, state: FSMContext):
    action = call.data.split(":")[1]
    data = await state.get_data()
    code = data.get("edit_code")

    if not code:
        await call.answer("❌ Kod topilmadi!", show_alert=True)
        return

    if action == "all":
        await update_episode_vip(code)
        await state.clear()
        await call.message.edit_text(
            f"✅ Kod {code} — barcha qismlar VIP qilindi!",
            reply_markup=back_admin_kb("bp_vip")
        )
    elif action == "clear":
        await clear_episode_vip(code)
        await state.clear()
        await call.message.edit_text(
            f"✅ Kod {code} — barcha qismlar oddiy qilindi!",
            reply_markup=back_admin_kb("bp_vip")
        )
    elif action == "from_ep":
        await state.set_state(AnimeEditStates.waiting_vip_ep_num)
        await call.message.edit_text(
            "🔢 1-faslda nechinchi qismdan boshlab VIP qilish?\n"
            "Masalan: 4 — 4-qismdan boshlab VIP\n\n"
            "Boshqa fasllarga tegmaydi.",
            reply_markup=cancel_admin_kb()
        )
    elif action == "from_season":
        await state.set_state(AnimeEditStates.waiting_vip_season_num)
        await call.message.edit_text(
            "📺 Nechinchi FASL butunlay VIP qilinsin?\n"
            "Masalan: 2 — 2-fasl butunlay VIP bo'ladi\n\n"
            "Faqat shu faslga tegadi, boshqa fasllar o'zgarmaydi.",
            reply_markup=cancel_admin_kb()
        )

@router.message(AnimeEditStates.waiting_vip_ep_num)
async def process_vip_ep_num(message: Message, state: FSMContext):
    try:
        ep_from = int(message.text.strip())
    except:
        await message.answer("❌ Faqat raqam!", reply_markup=cancel_admin_kb())
        return
    data = await state.get_data()
    code = data.get("edit_code")
    await update_episode_vip(code, from_episode=ep_from)
    await state.clear()
    await message.answer(
        f"✅ Kod {code} — 1-faslda {ep_from}-qismdan boshlab VIP qilindi!\n"
        f"(Boshqa fasllar o'zgarmadi)",
        reply_markup=back_admin_kb("bp_vip")
    )

@router.message(AnimeEditStates.waiting_vip_season_num)
async def process_vip_season_num(message: Message, state: FSMContext):
    try:
        season_from = int(message.text.strip())
    except:
        await message.answer("❌ Faqat raqam!", reply_markup=cancel_admin_kb())
        return
    data = await state.get_data()
    code = data.get("edit_code")
    await update_episode_vip(code, from_season=season_from)
    await state.clear()
    await message.answer(
        f"✅ Kod {code} — {season_from}-fasl butunlay VIP qilindi!\n"
        f"(Boshqa fasllar o'zgarmadi)",
        reply_markup=back_admin_kb("bp_vip")
    )
