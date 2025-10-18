import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # env variables
    ACCESS_TOKEN = os.getenv("LINE_BOT_CHANNEL_ACCESS_TOKEN")
    CHANNEL_SECRET = os.getenv("LINE_BOT_CHANNEL_SECRET")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    GOOGLE_GEMENI_API_KEY = os.getenv("GOOGLE_GEMENI_API_KEY")
    IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL")
    FROM_BASE_URL = os.getenv("FROM_BASE_URL")
    LIFF_ID = os.getenv("LIFF_ID")
    
config = Config()