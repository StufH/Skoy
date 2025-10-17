from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import uuid
import sqlite3
import qrcode
from PIL import Image
import shutil
import json
import os

from .db import init_db, get_connection, ensure_dirs, STORAGE_DIR
from .models import CardOut, TopItem

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Ensure storage dirs exist before mounting static routes
ensure_dirs()

app = FastAPI(title="Russekort Maker")

# CORS/Trusted Hosts configurable via env
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins if o.strip()]
ALLOW_CREDS = False if ALLOWED_ORIGINS == ["*"] else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDS,
    allow_methods=["*"],
    allow_headers=["*"],
)

_raw_hosts = os.getenv("ALLOWED_HOSTS", "*")
if _raw_hosts and _raw_hosts.strip() != "*":
    allowed_hosts = [h.strip() for h in _raw_hosts.split(",") if h.strip()]
    if allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL")
MAX_MB = int(os.getenv("MAX_CONTENT_LENGTH_MB", "10"))
MAX_BYTES = MAX_MB * 1024 * 1024

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Basic hardening headers
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    # Allow camera on same-origin for scanner
    response.headers.setdefault("Permissions-Policy", "camera=(self)")
    # CSP tuned for this app
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data: blob:; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; media-src 'self' blob:;"
    )
    # HSTS if served over HTTPS
    if (request.headers.get("x-forwarded-proto") or request.url.scheme) == "https":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
    return response

@app.on_event("startup")
def on_startup():
    init_db()
    ensure_dirs()


# Static mounts
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# Serve media (uploaded images, qrcodes)
app.mount("/media", StaticFiles(directory=STORAGE_DIR), name="media")


@app.get("/", response_class=HTMLResponse)
async def index_root():
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.get("/card/{card_id}", response_class=HTMLResponse)
async def card_page(card_id: str):
    # Serve the SPA for deep links; the frontend will fetch the card and render
    index_path = STATIC_DIR / "index.html"
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.get("/api/health")
async def health():
    return {"ok": True, "time": datetime.utcnow().isoformat()}


@app.post("/api/cards", response_model=CardOut)
async def create_card(
    request: Request,
    display_name: Optional[str] = Form(None),
    russ_title: Optional[str] = Form(None),
    line: Optional[str] = Form(None),
    quote: Optional[str] = Form(None),
    contact_json: Optional[str] = Form(None),  # JSON dict with snapchat, instagram, etc.
    bg_color: Optional[str] = Form(None),
    text_color: Optional[str] = Form(None),
    font: Optional[str] = Form(None),
    stickers_json: Optional[str] = Form(None),  # JSON array of stickers placements
    image: Optional[UploadFile] = File(None),
):
    ensure_dirs()
    # Enforce request size limit
    try:
        clen = int(request.headers.get("content-length", "0"))
        if clen and clen > MAX_BYTES:
            raise HTTPException(status_code=413, detail=f"Payload too large. Max {MAX_MB}MB")
    except ValueError:
        pass

    card_id = uuid.uuid4().hex

    image_path: Optional[Path] = None
    if image is not None:
        # Validate extension
        ext = Path(image.filename or "").suffix.lower()
        if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
            raise HTTPException(status_code=400, detail="Only PNG/JPG/WEBP allowed")
        dest = STORAGE_DIR / "cards" / f"{card_id}{ext}"
        with dest.open("wb") as out:
            shutil.copyfileobj(image.file, out)
        # Validate content is an image
        try:
            with Image.open(dest) as im:
                im.verify()
        except Exception:
            try:
                dest.unlink()
            except Exception:
                pass
            raise HTTPException(status_code=400, detail="Invalid image upload")
        image_path = dest

    contact = None
    if contact_json:
        try:
            contact = json.loads(contact_json)
        except Exception:
            contact = None

    stickers = None
    if stickers_json:
        try:
            stickers = json.loads(stickers_json)
        except Exception:
            stickers = None

    created_at = datetime.utcnow().isoformat()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO cards (
                id, display_name, russ_title, line, quote, contact,
                bg_color, text_color, font, stickers, image_path, created_at, scan_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0);
            """,
            (
                card_id,
                display_name,
                russ_title,
                line,
                quote,
                json.dumps(contact, ensure_ascii=False) if contact else None,
                bg_color,
                text_color,
                font,
                json.dumps(stickers, ensure_ascii=False) if stickers else None,
                str(image_path) if image_path else None,
                created_at,
            ),
        )
        conn.commit()

    return await get_card(request, card_id)


@app.get("/api/cards/{card_id}", response_model=CardOut)
async def get_card(request: Request, card_id: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Card not found")

        image_url = None
        if row["image_path"]:
            # expose through /media; compute relative to STORAGE_DIR
            try:
                p = Path(row["image_path"]).resolve()
                rel = p.relative_to(STORAGE_DIR)
                image_url = f"/media/{rel.as_posix()}"
            except Exception:
                image_url = None

        card = CardOut(
            id=row["id"],
            display_name=row["display_name"],
            russ_title=row["russ_title"],
            line=row["line"],
            quote=row["quote"],
            contact=(json.loads(row["contact"]) if row["contact"] else None),
            bg_color=row["bg_color"],
            text_color=row["text_color"],
            font=row["font"],
            stickers=(json.loads(row["stickers"]) if row["stickers"] else None),
            image_url=image_url,
            created_at=row["created_at"],
            scan_count=row["scan_count"],
        )
        return card


@app.get("/api/cards/{card_id}/qrcode")
async def get_qrcode(request: Request, card_id: str, force: int = 0):
    # Check card exists
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM cards WHERE id = ?", (card_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Card not found")

    # Compose target URL for the card page
    if PUBLIC_BASE_URL:
        url = f"{PUBLIC_BASE_URL.rstrip('/')}/card/{card_id}"
    else:
        host = request.headers.get("host")
        scheme = request.headers.get("x-forwarded-proto") or request.url.scheme
        url = f"{scheme}://{host}/card/{card_id}"

    out_path = STORAGE_DIR / "qrcodes" / f"{card_id}.png"
    if force == 1 and out_path.exists():
        try:
            out_path.unlink()
        except Exception:
            pass
    if not out_path.exists():
        img = qrcode.make(url)
        img.save(out_path)

    return FileResponse(out_path, media_type="image/png")


@app.post("/api/cards/{card_id}/scan")
async def increment_scan(card_id: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE cards SET scan_count = COALESCE(scan_count,0) + 1 WHERE id = ?", (card_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Card not found")
        conn.commit()
    return {"ok": True}


@app.get("/api/top", response_model=List[TopItem])
async def top_cards():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, display_name, scan_count, image_path FROM cards ORDER BY scan_count DESC, created_at ASC LIMIT 10"
        )
        items = []
        for row in cur.fetchall():
            image_url = None
            if row["image_path"]:
                try:
                    p = Path(row["image_path"]).resolve()
                    rel = p.relative_to(STORAGE_DIR)
                    image_url = f"/media/{rel.as_posix()}"
                except Exception:
                    image_url = None
            items.append(
                TopItem(
                    id=row["id"],
                    display_name=row["display_name"],
                    scan_count=row["scan_count"],
                    image_url=image_url,
                )
            )
        return items
