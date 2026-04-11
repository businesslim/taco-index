from app.config import Settings


def test_postgres_scheme_converted():
    result = Settings.fix_database_url("postgres://user:pass@host:5432/db")
    assert result == "postgresql+asyncpg://user:pass@host:5432/db"


def test_postgresql_scheme_converted():
    result = Settings.fix_database_url("postgresql://user:pass@host:5432/db")
    assert result == "postgresql+asyncpg://user:pass@host:5432/db"


def test_asyncpg_scheme_unchanged():
    result = Settings.fix_database_url("postgresql+asyncpg://user:pass@host:5432/db")
    assert result == "postgresql+asyncpg://user:pass@host:5432/db"
