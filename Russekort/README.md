# Russekort Maker (Digital)

A simple web app to design, generate, scan, and collect Russekort cards. Includes a Top 10 most-scanned leaderboard.

Features
- Create your own card with templates, colors, fonts, emoji stickers, and a photo.
- Generate a unique QR code linking to your card page.
- Built-in QR scanner (uses the browser's BarcodeDetector API). Fallback: upload a QR image.
- Album: Save scanned cards locally (offline) in your browser.
- Top 10: Leaderboard of most scanned cards.

Tech
- Backend: FastAPI + SQLite (sqlite3).
- Frontend: Vanilla HTML/CSS/JS. Canvas-based card renderer.

Quick start (Windows cmd)
1) Install deps
```
python -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r Russekort\requirements.txt
```

2) Run the dev server
```
.venv\Scripts\python -m uvicorn Russekort.backend.main:app --reload --host 0.0.0.0 --port 8000
```

3) Open
- http://localhost:8000 -> App
- http://localhost:8000/docs -> API docs

Notes
- Your album is stored in localStorage and available offline.
- QR scanner requires HTTPS for camera on some browsers; on Chrome desktop/mobile, http://localhost works. If your browser blocks the camera, try Chrome or host via HTTPS.
- Fonts: We use system fonts. For print quality, download your card PNG from the Create tab.

Project layout
```
Russekort/
  backend/
    main.py
    db.py
    models.py
    storage/               # generated at runtime
      cards/
      qrcodes/
  static/
    index.html
    style.css
    app.js
  requirements.txt
  README.md
```

License
- This project is for educational/personal use.

