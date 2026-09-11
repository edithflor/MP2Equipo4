from contextlib import asynccontextmanager

import pymysql
from fastapi import FastAPI
from minio import Minio

from dataset_quality.settings import Settings, get_settings


def storage_client(settings: Settings) -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def ensure_bucket(settings: Settings) -> None:
    client = storage_client(settings)
    if not client.bucket_exists(settings.minio_bucket):
        client.make_bucket(settings.minio_bucket)


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_bucket(get_settings())
    yield


app = FastAPI(title="Dataset Quality", version="0.1.0", lifespan=lifespan)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "dataset-quality", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health() -> dict[str, object]:
    settings = get_settings()
    database_ok = False
    storage_ok = False

    try:
        connection = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            connect_timeout=3,
        )
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        connection.close()
        database_ok = True
    except pymysql.MySQLError:
        database_ok = False

    try:
        storage_ok = storage_client(settings).bucket_exists(settings.minio_bucket)
    except Exception:  # noqa: BLE001 -- health endpoint debe reportar y no ocultar el resto
        storage_ok = False

    return {
        "ok": database_ok and storage_ok,
        "environment": settings.app_env,
        "services": {"database": database_ok, "storage": storage_ok},
        "database": settings.db_name,
        "bucket": settings.minio_bucket,
    }
