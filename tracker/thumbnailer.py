import os
from PIL import Image
from pdf2image import convert_from_path
import hashlib

THUMB_DIR = "thumbnails"
THUMB_SIZE = (256, 256)

os.makedirs(THUMB_DIR, exist_ok=True)

def _hash_path(path: str) -> str:
    return hashlib.md5(path.encode()).hexdigest()

def get_thumbnail_path(file_path: str) -> str:
    return os.path.join(THUMB_DIR, _hash_path(file_path) + ".png")

def generate_thumbnail(file_path: str) -> str | None:
    thumb_path = get_thumbnail_path(file_path)

    if os.path.exists(thumb_path):
        return thumb_path

    ext = os.path.splitext(file_path)[1].lower()

    try:
        # ---------- PDF ----------
        if ext == ".pdf":
            pages = convert_from_path(
                file_path,
                first_page=1,
                last_page=1,
                size=THUMB_SIZE
            )
            img = pages[0]
            img.save(thumb_path, "PNG")
            return thumb_path

        # ---------- IMAGE ----------
        if ext in [".png", ".jpg", ".jpeg", ".webp"]:
            img = Image.open(file_path)
            img.thumbnail(THUMB_SIZE)
            img.save(thumb_path, "PNG")
            return thumb_path

    except Exception as e:
        print("Thumbnail error:", e)

    return None
