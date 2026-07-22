import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'store.db'}")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

SECRET_KEY = os.getenv("SECRET_KEY", "shopgenius-change-this-key-in-production")
STORE_NAME = os.getenv("STORE_NAME", "ShopGenius Store")
STORE_TAGLINE = os.getenv("STORE_TAGLINE", "Find Products That Change Your Life")
AMAZON_PARTNER_TAG = os.getenv("AMAZON_PARTNER_TAG", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

CATEGORIES = [
    {"name": "Electronics", "slug": "electronics", "icon": "📱"},
    {"name": "Home & Kitchen", "slug": "home-kitchen", "icon": "🏠"},
    {"name": "Fashion", "slug": "fashion", "icon": "👜"},
    {"name": "Beauty", "slug": "beauty", "icon": "💄"},
    {"name": "Fitness", "slug": "fitness", "icon": "💪"},
    {"name": "Gaming", "slug": "gaming", "icon": "🎮"},
    {"name": "Pets", "slug": "pets", "icon": "🐕"},
    {"name": "Automotive", "slug": "automotive", "icon": "🚗"},
]
