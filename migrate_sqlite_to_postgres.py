import asyncio
import aiosqlite
import asyncpg
import os
from datetime import datetime


SQLITE_DB = "anime_bot.db"
POSTGRES_URL = os.getenv("DATABASE_URL")


async def migrate():
    if not POSTGRES_URL:
        raise Exception("DATABASE_URL topilmadi")

    pg = await asyncpg.connect(POSTGRES_URL)

    sqlite = await aiosqlite.connect(SQLITE_DB)
    sqlite.row_factory = aiosqlite.Row

    print("Migration boshlandi...")

    tables = [
        "users",
        "animes",
        "seasons",
        "episodes",
        "channels",
        "vip_cards",
        "vip_orders",
        "admins",
        "bot_settings",
        "promo_codes",
        "broadcast_logs",
        "user_watched",
        "join_requests"
    ]

    for table in tables:
        print(f"Ko'chirilmoqda: {table}")

        rows = await sqlite.execute_fetchall(
            f"SELECT * FROM {table}"
        )

        if rows:
            columns = rows[0].keys()

            placeholders = ", ".join(
                f"${i+1}" for i in range(len(columns))
            )

            query = f"""
            INSERT INTO {table}
            ({','.join(columns)})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
            """

            for row in rows:
                values = []

                for c in columns:
                    value = row[c]

                    # SQLite TEXT vaqtlarini PostgreSQL TIMESTAMP ga o'tkazish
                    if c in [
                        "joined_at",
                        "last_active",
                        "created_at",
                        "updated_at",
                        "added_at",
                        "watched_at",
                        "requested_at"
                    ] and isinstance(value, str):

                        try:
                            value = datetime.fromisoformat(value)
                        except:
                            pass

                    values.append(value)

                await pg.execute(
                    query,
                    *values
                )

        print(f"{table} tayyor")

    await sqlite.close()
    await pg.close()

    print("✅ Migration tugadi")


asyncio.run(migrate())