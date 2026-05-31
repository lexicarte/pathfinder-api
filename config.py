import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not OPENAI_API_KEY:
    raise Exception("Missing OPENAI_API_KEY")

if not ADZUNA_APP_ID:
    raise Exception("Missing ADZUNA_APP_ID")

if not ADZUNA_APP_KEY:
    raise Exception("Missing ADZUNA_APP_KEY")
