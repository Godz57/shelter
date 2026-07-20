"""Django settings for Shelter."""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

load_dotenv()
# Vercel CLI `vercel pull` writes here for local use
load_dotenv(".env.local", override=False)

BASE_DIR = Path(__file__).resolve().parent.parent

# Vercel sets VERCEL=1 on the platform
ON_VERCEL = bool(os.environ.get("VERCEL"))

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-insecure-change-me-before-production",
)
if ON_VERCEL and SECRET_KEY == "dev-insecure-change-me-before-production":
    raise RuntimeError("Set DJANGO_SECRET_KEY in Vercel project environment variables.")

DEBUG = os.environ.get("DJANGO_DEBUG", "0" if ON_VERCEL else "1") == "1"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]
# Automatic hosts from Vercel deployment URLs
for env_key in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
    host = (os.environ.get(env_key) or "").strip()
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)
if ON_VERCEL and ".vercel.app" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(".vercel.app")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "catalog.apps.CatalogConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    # Serverless: no persistent connections between invocations
    conn_max_age = 0 if ON_VERCEL else 600
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=conn_max_age,
            ssl_require=ON_VERCEL,
        )
    }
else:
    if ON_VERCEL:
        raise RuntimeError(
            "DATABASE_URL is required on Vercel. "
            "Add a Postgres store (e.g. Neon) and set DATABASE_URL."
        )
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "catalog:home"  # fallback; staff handled in ShelterLoginView
LOGOUT_REDIRECT_URL = "catalog:home"
LOGIN_URL = "login"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
}

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]
for env_key in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
    host = (os.environ.get(env_key) or "").strip()
    if host:
        origin = host if host.startswith("http") else f"https://{host}"
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)

if not DEBUG or ON_VERCEL:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
