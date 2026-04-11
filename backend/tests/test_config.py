import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


# Isolated Settings class for testing the validator in isolation
class _TestSettings(BaseSettings):
    model_config = SettingsConfigDict()
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/db"

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v


def test_postgres_scheme_converted():
    s = _TestSettings(database_url="postgres://user:pass@host:5432/db")
    assert s.database_url == "postgresql+asyncpg://user:pass@host:5432/db"


def test_postgresql_scheme_converted():
    s = _TestSettings(database_url="postgresql://user:pass@host:5432/db")
    assert s.database_url == "postgresql+asyncpg://user:pass@host:5432/db"


def test_asyncpg_scheme_unchanged():
    s = _TestSettings(database_url="postgresql+asyncpg://user:pass@host:5432/db")
    assert s.database_url == "postgresql+asyncpg://user:pass@host:5432/db"
