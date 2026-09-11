import pytest
from pydantic import ValidationError

from dataset_quality.settings import Settings


def test_settings_accept_local_services() -> None:
    settings = Settings(
        db_password="secret-for-test",
        minio_access_key="test-user",
        minio_secret_key="secret-for-test",
    )

    assert settings.db_port == 3306
    assert settings.minio_secure is False


def test_settings_reject_empty_database_password() -> None:
    with pytest.raises(ValidationError):
        Settings(
            db_password="",
            minio_access_key="test-user",
            minio_secret_key="secret-for-test",
        )


def test_settings_reject_invalid_port() -> None:
    with pytest.raises(ValidationError):
        Settings(
            db_port=70_000,
            db_password="secret-for-test",
            minio_access_key="test-user",
            minio_secret_key="secret-for-test",
        )
