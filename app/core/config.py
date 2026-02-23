import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(ENV_PATH)

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/MenuApp').strip()
JWT_SECRET = os.getenv('JWT_SECRET', 'change-me').strip()
JWT_ALGORITHM = 'HS256'
JWT_EXP_DAYS = int(os.getenv('JWT_EXP_DAYS', '7'))
FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173').strip().rstrip('/')
