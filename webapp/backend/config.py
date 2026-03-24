import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.environ.get("DB_PATH", "hermes.db")
CUSTOMER_DATA_DIR = os.environ.get("CUSTOMER_DATA_DIR", "/home/hermes/data")
PORT = os.environ.get("PORT", "5000")
BUSINESS_NAME = os.environ.get("BUSINESS_NAME", "Business Name Here")
NANOBOT_SOCKET = os.environ.get("NANOBOT_SOCKET", "/home/hermes/data/nanobot.sock")
