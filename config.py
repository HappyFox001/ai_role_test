import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")
GEMINI_OPENAI_BASE_URL = os.getenv("GEMINI_OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# Application Settings
MAX_CONVERSATION_ROUNDS = int(os.getenv("MAX_CONVERSATION_ROUNDS", "30"))
CONVERSATION_HISTORY_FILE = os.getenv("CONVERSATION_HISTORY_FILE", "conversation_history.json")
STREAM_CHUNK_SIZE = int(os.getenv("STREAM_CHUNK_SIZE", "50"))

# Emotion and State Configuration
EMOTIONS = [
    "Joy", "Anticipation", "Anger", "Disgust", 
    "Sadness", "Surprise", "Fear", "Trust"
]

STATES = [
    "Serenity", "Interest", "Annoyance", "Boredom", 
    "Pensiveness", "Anxiety", "Morbidness", "Ecstasy", 
    "Curiosity", "Distraction"
]