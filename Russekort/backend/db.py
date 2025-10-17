import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional
import json

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "backend" / "storage"
DB_PATH = STORAGE_DIR / "app.db"


def ensure_dirs() -> None:
    (STORAGE_DIR / "cards").mkdir(parents=True, exist_ok=True)
    (STORAGE_DIR / "qrcodes").mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    ensure_dirs()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                display_name TEXT,
                russ_title TEXT,
                line TEXT,
                quote TEXT,
                contact TEXT, -- JSON
                bg_color TEXT,
                text_color TEXT,
                font TEXT,
                stickers TEXT, -- JSON array
                image_path TEXT,
                created_at TEXT,
                scan_count INTEGER DEFAULT 0
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_cards_scan_count ON cards (scan_count DESC);")
        conn.commit()


def to_json_str(data: Optional[Dict[str, Any]]) -> Optional[str]:
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False)


def from_json_str(s: Optional[str]) -> Optional[Dict[str, Any]]:
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None

