# tracker/config.py (macOS-safe)

import os
import sys
from dotenv import load_dotenv

def get_base_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

BASE_DIR = get_base_dir()

dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

VALID_EXTENSIONS = (".txt", ".md", ".py", ".csv", ".docx", ".pdf")

EXCLUDED_DIRS = [
    "Library", "System", "Applications",
    "__pycache__", "node_modules", ".git",
    ".vscode", ".idea", ".Trash", ".DS_Store",
    "db", "dist", "model", ".venv", "venv", "env"
]

DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "metadata.db")

EMBEDDINGS_PATH = os.path.join(DB_DIR, "embeddings")

SETTINGS_PATH = os.path.join(DB_DIR, "settings.json")

API_KEY = os.environ.get("GOOGLE_API_KEY")
