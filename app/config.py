import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # The official google-genai library automatically checks for GEMINI_API_KEY
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/tasks.db")
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "CRITICAL CONFIG ERROR: 'GEMINI_API_KEY' environment variable is missing. "
                "Please generate a free developer key at Google AI Studio."
            )