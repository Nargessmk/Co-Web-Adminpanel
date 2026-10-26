# Cloudland-Software-Resume

Quasar (Vue 3) frontend + Node/Express backend + PostgreSQL/Redis, deployed with Docker Compose.
Admin authentication runs through the FastAPI auth microservice → FusionAuth (`auth.ailand.ai`).

---

## Project layout

```
├── docker-compose.yml            # all services + networks + volumes
├── deploy.sh                     # one-shot deployment script
├── .env.example                  # template → copy to .env and edit
├── api/backend/                  # Node/Express API (port 3000)
│   ├── Dockerfile
│   └── db/init.sql               # DB schema, auto-loaded on first run
├── style/frontend/               # Quasar SPA served by nginx (port 80)
│   ├── Dockerfile
│   └── nginx.conf                # serves SPA, proxies /api + /uploads to backend
└── api/CloudLand-FastAPI-Main-Microservices/   # auth + gateway (4001/4002)
```

Only **nginx (port 80)** is exposed publicly. All other services (backend, postgres,
redis, gateway, auth) are bound to `127.0.0.1` on the host and talk to each other on
the internal Docker network.

---

## Deploy on a server (step by step)

### 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
docker compose version   # must print a version
```

### 2. Get the code

```bash
git clone https://github.com/Cloudland-Main/Cloudland-Software-Resume.git
cd Cloudland-Software-Resume
```

### 3. Create the `.env` file

```bash
cp .env.example .env
nano .env
```

**You MUST change these before starting:**

| Variable | What to put |
|----------|-------------|
| `DB_PASSWORD` | any long random string (e.g. `openssl rand -hex 16`) |
| `MICROSERVICE_JWT_SECRET` | must match the value used by the auth microservice |
| `FUSIONAUTH_API_KEY` / `FUSIONAUTH_APPLICATION_ID` | real FusionAuth values |

> `.env` is git-ignored — never commit it, never send it through chat.

### 4. Build & start

```bash
docker compose up -d --build
```

This starts: `postgres`, `redis`, `backend`, `frontend`, `gateway`, `auth`.
The database schema (`api/backend/db/init.sql`) is created automatically on first run.

### 5. Verify everything works

```bash
docker compose ps                      # all containers "Up", postgres/redis "healthy"

curl http://localhost/api/health       # → {"success":true,...}
curl -I http://localhost/              # → 200
curl -I http://localhost/admin/login   # → 200 (SPA fallback)

# login chain (backend → auth microservice → FusionAuth):
curl -X POST http://localhost/api/auth/login \
     -H 'Content-Type: application/json' \
     -d '{"username":"test","password":"wrong"}'
# → {"success":false,"message":"Invalid credentials"} = chain works
#   (use real admin credentials to actually log in)
```

Then open `http://<server-ip>/` in a browser and log in at `http://<server-ip>/admin/login`.

### 6. Day-2 operations

```bash
docker compose logs -f backend      # follow logs
docker compose restart backend      # restart one service
docker compose up -d --build        # rebuild after code changes
docker compose down                 # stop (data survives in volumes)
docker compose down -v              # stop AND wipe database (careful!)
```

---

## Optional microservices

`app-management`, `storage`, `background-task` and `rabbitmq` need extra
infrastructure (MinIO/S3, Elasticsearch) and are disabled by default:

```bash
docker compose --profile extra up -d
```

---

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Backend restart-loops | `docker compose logs backend` — usually DB password mismatch between `.env` and existing volume. After changing `DB_PASSWORD` run `docker compose down -v` (wipes DB!) |
| Login always fails with 500 | auth/gateway containers down, or `MICROSERVICE_JWT_SECRET` mismatch — `docker compose logs auth gateway` |
| Product images 404 | uploads live in the `uploads_data` volume; only the backend writes there |
| Changed code but no effect | `docker compose up -d --build frontend` (rebuild is not automatic) |
