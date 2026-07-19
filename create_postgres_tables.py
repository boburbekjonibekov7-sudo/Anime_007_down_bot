import asyncio
import asyncpg
import os


DATABASE_URL = os.getenv("DATABASE_URL")


async def create_tables():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL topilmadi")

    db = await asyncpg.connect(DATABASE_URL)

    print("PostgreSQL ga ulandi...")

    await db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        user_id BIGINT UNIQUE NOT NULL,
        username TEXT,
        full_name TEXT,
        is_banned INTEGER DEFAULT 0,
        is_vip INTEGER DEFAULT 0,
        vip_until TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS animes (
        id SERIAL PRIMARY KEY,
        code INTEGER UNIQUE NOT NULL,
        name TEXT NOT NULL,
        genre TEXT,
        studio TEXT,
        poster_file_id TEXT,
        is_vip INTEGER DEFAULT 0,
        vip_from_episode INTEGER DEFAULT 0,
        vip_from_season INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        forward_status INTEGER DEFAULT 1,
        search_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS seasons (
        id SERIAL PRIMARY KEY,
        anime_code INTEGER NOT NULL,
        season_number INTEGER NOT NULL,
        season_name TEXT,
        UNIQUE(anime_code, season_number)
    );


    CREATE TABLE IF NOT EXISTS episodes (
        id SERIAL PRIMARY KEY,
        anime_code INTEGER NOT NULL,
        season_number INTEGER DEFAULT 1,
        episode_number INTEGER NOT NULL,
        file_id TEXT NOT NULL,
        thumbnail_file_id TEXT,
        is_vip INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS channels (
        id SERIAL PRIMARY KEY,
        channel_id TEXT UNIQUE NOT NULL,
        channel_username TEXT,
        channel_name TEXT,
        channel_type TEXT DEFAULT 'public',
        channel_url TEXT,
        is_main INTEGER DEFAULT 0,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS admins (
        id SERIAL PRIMARY KEY,
        user_id BIGINT UNIQUE NOT NULL,
        username TEXT,
        full_name TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS bot_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );


    CREATE TABLE IF NOT EXISTS vip_cards (
        id SERIAL PRIMARY KEY,
        card_number TEXT NOT NULL,
        card_type TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS vip_orders (
        id SERIAL PRIMARY KEY,
        order_id TEXT UNIQUE NOT NULL,
        user_id BIGINT NOT NULL,
        duration_days INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        card_id INTEGER,
        status TEXT DEFAULT 'pending',
        receipt_file_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS promo_codes (
        id SERIAL PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        duration_days INTEGER DEFAULT 7,
        is_active INTEGER DEFAULT 1,
        used_by TEXT DEFAULT '[]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TEXT
    );


    CREATE TABLE IF NOT EXISTS broadcast_logs (
        id SERIAL PRIMARY KEY,
        admin_id BIGINT,
        message_type TEXT,
        recipients_count INTEGER,
        sent_count INTEGER,
        failed_count INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );


    CREATE TABLE IF NOT EXISTS user_watched (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        anime_code INTEGER NOT NULL,
        episode_number INTEGER NOT NULL,
        season_number INTEGER DEFAULT 1,
        watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, anime_code, episode_number, season_number)
    );


    CREATE TABLE IF NOT EXISTS join_requests (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        channel_id TEXT NOT NULL,
        requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, channel_id)
    );
    """)

    await db.close()

    print("✅ PostgreSQL jadvallari yaratildi!")


asyncio.run(create_tables())