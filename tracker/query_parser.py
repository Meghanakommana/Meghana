import re
from datetime import datetime, timedelta

def parse_query(q: str):
    q = q.lower()

    data = {
        "action": "any",
        "date_from": None,
        "date_to": None,
        "file_type": None,
        "keywords": None,
        "semantic": q
    }

    # -------- ACTION --------
    if "opened" or "open" in q:
        data["action"] = "opened"
    elif "created"  in q:
        data["action"] = "created"
    elif "modified"  or "edited"in q:
        data["action"] = "modified"

    # -------- RELATIVE DATES --------
    now = datetime.now()

    if "today" in q:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        data["date_from"] = start.timestamp()
        data["date_to"] = now.timestamp()

    elif "yesterday" in q:
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=1)
        data["date_from"] = start.timestamp()
        data["date_to"] = end.timestamp()

    # 4 days ago
    m = re.search(r"(\d+)\s+days?\s+ago", q)
    if m:
        days = int(m.group(1))
        start = now - timedelta(days=days)
        data["date_from"] = start.timestamp()

    # -------- FILE TYPE --------
    ext = re.search(r"\.(pdf|py|txt|md|csv|docx)", q)
    if ext:
        data["file_type"] = ext.group(1)

    return data
