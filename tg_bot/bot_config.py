import os
import sys

from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))


load_dotenv(os.path.join(BASE_DIR, ".env"))



BOT_TOKEN = os.getenv("BOT_TOKEN")


REDIS_URL = os.getenv("REDIS_URL")