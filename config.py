from os import getenv

from dotenv import load_dotenv

load_dotenv()

TGBOT_TOKEN = getenv("TGBOT_TOKEN")
TG_CHAT = getenv("TG_CHAT")
