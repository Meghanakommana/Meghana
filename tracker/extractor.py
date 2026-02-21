# tracker/extractor.py

import os
from docx import Document
import logging 
logging.getLogger("pdfminer").setLevel(logging.ERROR)

try:
    import pdfplumber
except Exception:
    pdfplumber = None

def extract_text(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext in [".txt", ".md", ".py", ".csv"]:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        if ext == ".docx":
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)

        if ext == ".pdf" and pdfplumber:
            text = []
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text.append(t)
            return "\n".join(text)

    except Exception:
        pass

    return ""
