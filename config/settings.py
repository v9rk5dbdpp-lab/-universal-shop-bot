import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_ids: set[int]
    database_path: str


raw_admin_ids = os.getenv("ADMIN_IDS", "")
admin_ids = {
    int(admin_id.strip())
    for admin_id in raw_admin_ids.split(",")
    if admin_id.strip().isdigit()
}

settings = Settings(
    bot_token=os.getenv("BOT_TOKEN", ""),
    admin_ids=admin_ids,
    database_path=os.getenv("DATABASE_PATH", "shop.db"),
)

if not settings.bot_token:
    raise RuntimeError("BOT_TOKEN is not set. Add it to .env file.")
