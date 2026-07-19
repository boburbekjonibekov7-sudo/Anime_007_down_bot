# config.py
import os
from dataclasses import dataclass, field

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    ADMIN_IDS: list = None
    DB_PATH: str = "anime_bot.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Rate limiting
    RATE_LIMIT: float = 0.5        # seconds between messages
    BROADCAST_DELAY: float = 0.05  # seconds between broadcast messages

    # Pagination
    EPISODES_PER_PAGE: int = 24
    ANIMES_PER_PAGE: int = 8

    def __post_init__(self):
        if self.ADMIN_IDS is None:
            self.ADMIN_IDS = [
                int(x) for x in os.getenv("ADMIN_IDS", "7538793043").split(",")
            ]

config = Config()
