import csv
import os

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repositories.csv")

COLUMN_DEFS = [
    ("ID",          "id",          "int"),
    ("Name",        "name",        "text"),
    ("Full Name",   "full_name",   "text"),
    ("Description", "description", "text"),
    ("Language",    "language",    "text"),
    ("Stars",       "stars",       "int"),
    ("Forks",       "forks",       "int"),
    ("Open Issues", "open_issues", "int"),
    ("Created",     "created_at",  "date"),
    ("Updated",     "updated_at",  "date"),
    ("URL",         "html_url",    "text"),
]
HEADERS = [h for h, _, _ in COLUMN_DEFS]
FIELD_OF = {h: f for h, f, _ in COLUMN_DEFS}   # "Stars" -> "stars"
TYPE_OF = {h: t for h, _, t in COLUMN_DEFS}    # "Stars" -> "int"


def clean_row(raw):
    """Turn one CSV/scraper row into a dict with proper Python types."""
    row = {}
    for _, field, kind in COLUMN_DEFS:
        value = raw.get(field)
        if kind == "int":
            try:
                row[field] = int(value)
            except (TypeError, ValueError):
                row[field] = 0
        else:
            row[field] = "" if value is None else str(value)
    return row


def load_csv(path=CSV_FILE):
    """Read repositories.csv and return a list of row dicts."""
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", newline="", encoding="utf-8-sig") as f:
        for raw in csv.DictReader(f):
            rows.append(clean_row(raw))
    return rows
