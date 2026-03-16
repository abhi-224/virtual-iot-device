# conf.py
import os
from dotenv import load_dotenv

load_dotenv()

BROKER = os.getenv("BROKER")
PORT = int(os.getenv("PORT", 1883))
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
LATITUDE = float(os.getenv("LATITUDE", 0.0))
LONGITUDE = float(os.getenv("LONGITUDE", 0.0))
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", 5))
DB = os.getenv("DB")
TOPIC = "v1/devices/me/telemetry"
