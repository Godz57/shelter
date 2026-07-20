# Shelter

A small **gospel-publishing catalog** built with **Django** for portfolio use.

**Shelter** (as in *abrigo*) demonstrates the same web patterns used by content/publishing products: catalog models, staff admin, search and filters, authenticated reading lists, and a thin read-only JSON API — server-rendered with Django templates (no SPA).

> **Disclaimer:** Fictional titles and authors only. **Not affiliated with Crossway** or any publisher. Built as a learning / portfolio project for a Web Developer (Django) candidacy.

## Features

- Book catalog with authors, categories, featured flags, and cover images
- Public home, book list, book detail, author detail
- Search (title / subtitle / description / author), category filter, sort
- **Site-styled staff manage panel** at `/manage/` (add / edit / delete books, authors, categories)
- `/admin/` redirects to `/manage/` (legacy Django Admin UI not exposed)
- Sign up / log in / log out
- **Your Shelter** personal reading list (add / remove)
- Read-only JSON API: `GET /api/books/`, `GET /api/books/<slug>/`
- Seed command with sample data and cover URLs
- Postgres-ready settings, WhiteNoise static files, Gunicorn `Procfile`
- Automated tests (`python manage.py test`)

## Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.12+ |
| Framework | Django 5.2 |
| API | Django REST Framework |
| DB (dev) | SQLite |
| DB (prod) | PostgreSQL via `DATABASE_URL` |
| Static | WhiteNoise |
| Server | Gunicorn |

## Local setup

```powershell
cd shelf
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_catalog
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Tests

```powershell
python manage.py test
```

## API examples

```bash
curl http://127.0.0.1:8000/api/books/
curl http://127.0.0.1:8000/api/books/grace-and-truth/
```

## Project layout

```
config/          # settings, root URLs, WSGI
catalog/         # models, public views, /manage/ staff panel, API, seed, tests
templates/       # base + catalog + registration templates
static/css/      # site styles
```

## Deploy (Vercel)

Django is detected via `manage.py`. Static files are collected automatically; `build.py` runs migrations + seed.

### 1. Postgres (required)

Vercel has no durable disk — use **Neon**, **Vercel Postgres**, or **Supabase**. Copy the connection string as `DATABASE_URL`.

### 2. Environment variables (Vercel project)

| Variable | Value |
|----------|--------|
| `DJANGO_SECRET_KEY` | long random string |
| `DJANGO_DEBUG` | `0` |
| `DATABASE_URL` | `postgres://…` |
| `DJANGO_SUPERUSER_USERNAME` | `admin` (optional, default `admin`) |
| `DJANGO_SUPERUSER_PASSWORD` | set a real password in production |

`VERCEL_URL` / hosts are handled in settings for `.vercel.app`.

### 3. CLI

```bash
npm i -g vercel
cd shelf
vercel link
vercel env add DJANGO_SECRET_KEY
vercel env add DATABASE_URL
vercel env add DJANGO_DEBUG
vercel --prod
```

Or connect the GitHub repo `Godz57/shelf` in the Vercel dashboard (root = repo root).

### 4. After deploy

- Public site: `https://<project>.vercel.app/`
- Staff login: same **Log in** → user `admin` (lands on `/manage/`)

## Why this project

Crossway-style products are content-heavy web apps: catalogs, admin tooling, accounts, and APIs. Shelter is a focused exercise in those Django fundamentals — honest portfolio evidence, not a claim of years of production Django tenure.

## License

MIT — use and adapt freely for your own portfolio.
