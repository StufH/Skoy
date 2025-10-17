# Deploy Russekort Digital

This app is a FastAPI backend with a static frontend. To make QR codes work "anywhere on any phone," you must host it on a public HTTPS URL. Below are two good options:

- Option A (easiest hosted): Google Cloud Run (HTTPS, scales automatically). Note: Local SQLite storage will be ephemeral; for production, use a managed DB and object storage.
- Option B (simple VPS): Docker + docker-compose on a VM with a persistent volume.

Important: Storage and persistence
- The current app uses SQLite (file) and stores uploads/QRs under `Russekort/backend/storage`. On stateless platforms (Cloud Run), this data resets across deployments and instance restarts.
- For a demo or small event, Cloud Run is fine. For persistent data, either:
  - Switch to a managed database (Cloud SQL Postgres/MySQL) and a bucket (Cloud Storage) for images/QRs, or
  - Use a VPS with a mounted volume to persist `backend/storage`.

Regenerating QR after deploying to a new domain
- QR codes contain the full URL (scheme + host). After you deploy, use:
  - GET `/api/cards/{card_id}/qrcode?force=1` to regenerate the QR so it points at the new public domain.

---

Option A: Google Cloud Run

Prereqs
- Install Google Cloud SDK and authenticate: https://cloud.google.com/sdk
- Create/select a project and enable Cloud Run and Artifact Registry/APIs.

Build and deploy (from repo root)

```cmd
REM Set your variables
set GCP_PROJECT=YOUR_PROJECT_ID
set REGION=europe-north1
set SERVICE=russekort

REM Configure gcloud
gcloud config set project %GCP_PROJECT%
gcloud config set run/region %REGION%

REM Build and push image (Artifact Registry)
gcloud services enable artifactregistry.googleapis.com
set REPO=russekort-repo
set IMAGE=eu-north1-docker.pkg.dev/%GCP_PROJECT%/%REPO%/%SERVICE%:v1

gcloud artifacts repositories create %REPO% --repository-format=docker --location=%REGION% --description="Russekort images"

gcloud builds submit --tag %IMAGE% .

REM Deploy to Cloud Run (public)
gcloud run deploy %SERVICE% --image %IMAGE% --allow-unauthenticated --port 8080
```

After deploy
- gcloud prints a service URL like `https://russekort-xxxxxx-uc.a.run.app`
- Open that URL in your browser.
- Create a card and use the generated QR. It should scan on any phone.
- If you created QRs before deployment, regenerate them with `?force=1`.

Custom domain (optional)
- Map your domain: https://cloud.google.com/run/docs/mapping-custom-domains
- After your domain works, regenerate QRs (`?force=1`) so they embed the custom domain.

Notes
- Cloud Run storage is ephemeral. If you need persistence, see Option B or migrate to managed services.
- HTTPS terminates at Cloud Run; we already respect `X-Forwarded-Proto` for correct QR scheme.

---

Option B: VPS (Docker + Compose + persistent volume)

Prereqs
- A Linux VM (e.g., a small Ubuntu server) with Docker and docker-compose installed.
- A domain (optional). Use a reverse proxy for HTTPS (Caddy or Nginx + certbot).

Copy the repo to the server and run:

```bash
# On the server
sudo mkdir -p /opt/russekort_storage
sudo chown $USER:$USER /opt/russekort_storage

# From the repo root (where docker-compose.yml is)
docker compose up -d --build
```

This maps `/opt/russekort_storage` to `Russekort/backend/storage` in the container, so cards and QRs persist across restarts.

Default:
- App listens on container 8080 and host port 8080 (change in compose if needed).
- Access via http://YOUR_SERVER_IP:8080
- Put it behind a reverse proxy for HTTPS so the in-app QR scanner works reliably on all browsers.

---

Troubleshooting
- Scanner requires camera permissions and typically HTTPS. On Chrome (Android/iOS), it should work. On Safari, support for `BarcodeDetector` may vary; if blocked, users can still scan printed/displayed QR with their camera app to open the card.
- If QRs open the wrong domain, regenerate with `?force=1` after deployment or domain change.
- If the Top 10/album appears empty after redeploy on Cloud Run, it’s due to ephemeral storage; use a persistent setup if you need data durability.

