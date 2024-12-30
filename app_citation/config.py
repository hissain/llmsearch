# config.py

import os
from dotenv import load_dotenv

load_dotenv()

# Ensure this is set globally
os.environ["UVLOOP_DISABLE"] = "1"

# Configuration for external APIs
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
