import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-32-chars-min")

import pytest_asyncio
from app.core.auth import TokenPayload, get_viewer, get_operator
from app.core.database import Base, get_db
from app.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestAsyncSessionMaker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


TEST_USER = TokenPayload(
    sub="test-user-id",
    email="test@example.com",
    preferred_username="testuser",
    realm_access={"roles": ["viewer", "operator", "admin"]},
    resource_access={},
    exp=9999999999,
    iat=0,
    iss="http://test/realms/test",
    aud="test-client",
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestAsyncSessionMaker() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncClient:
    def override_get_db():
        yield db_session

    async def override_get_viewer():
        return TEST_USER

    async def override_get_operator():
        return TEST_USER

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_viewer] = override_get_viewer
    app.dependency_overrides[get_operator] = override_get_operator
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
