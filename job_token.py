import time
import hmac
import hashlib
import base64
import requests
import os
from dotenv import load_dotenv

from main import app

load_dotenv()

SMILE_PARTNER_ID = os.getenv("SMILE_PARTNER_ID")
SMILE_API_KEY = os.getenv("SMILE_API_KEY")
SMILE_BASE_URL = os.getenv("SMILE_BASE_URL")

if not SMILE_PARTNER_ID or not SMILE_API_KEY or not SMILE_BASE_URL:
    raise RuntimeError("Missing SMILE_PARTNER_ID or SMILE_API_KEY or SMILE_BASE_URL in .env")


