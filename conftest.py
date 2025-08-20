import pytest
from fastapi.testclient import TestClient
from main import app as fastapi_app
from app.services.ocr_service import OCRService
import os

@pytest.fixture(scope="module")
def app():
    """
    Fixture to provide a TestClient instance for the FastAPI application.
    Scope is 'module' to create one client per test module.
    """
    with TestClient(fastapi_app) as client:
        yield client

@pytest.fixture(scope="module")
def image_path():
    """
    Fixture to provide the path to the test nutrition label image.
    """
    # Check for the image in the root directory or in the 'uploads' directory
    path_in_root = "test_nutrition_label.png"
    path_in_uploads = os.path.join("uploads", "test_nutrition_label.png")

    if os.path.exists(path_in_root):
        return path_in_root
    elif os.path.exists(path_in_uploads):
        return path_in_uploads
    else:
        # If the image doesn't exist, we can't run the OCR tests.
        # Pytest will report this as a skip.
        pytest.skip("Test image 'test_nutrition_label.png' not found.")

@pytest.fixture(scope="module")
def ocr_service():
    """
    Fixture to provide an instance of the OCRService.
    """
    return OCRService()


# ===========================================
# Database Fixtures
# ===========================================

import app.models # Import all models to ensure they are registered with Base
from app.core.database import SessionLocal, Base, engine

@pytest.fixture(scope="session")
def db_engine(request):
    """
    Session-scoped fixture to manage the test database.
    Creates all tables before the test session starts and drops them after.
    """
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Function-scoped fixture to provide a clean database session for each test.
    Uses a transaction that is rolled back after each test to ensure isolation.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

# ===========================================
# Authentication and Session Fixtures
# ===========================================
import fakeredis
from unittest.mock import patch
from app.models.user import User, UserStatus
from app.api.auth import create_access_token
from app.services.session_service import SessionService

@pytest.fixture(scope="session", autouse=True)
def mock_redis(request):
    """
    Session-scoped fixture to mock the Redis client for all tests.
    `autouse=True` ensures it's activated for the whole session.
    """
    server = fakeredis.FakeServer()
    fake_redis_client = fakeredis.FakeRedis(server=server)

    with patch("app.core.database.redis_client", fake_redis_client):
        yield

@pytest.fixture(scope="function")
def test_user(db_session):
    """
    Fixture to create a test user in the database.
    """
    user = User(
        username="testuser",
        email="test@example.com",
        nickname="Test User"
    )
    user.set_password("testpassword")
    user.status = UserStatus.ACTIVE

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def token(test_user):
    """
    Fixture to create a JWT access token for the test_user.
    """
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return access_token

@pytest.fixture(scope="function")
async def session_id(test_user):
    """
    Fixture to create a session in the (mocked) Redis for the test_user.
    """
    session_service = SessionService()
    sid = await session_service.create_session(
        user_id=test_user.id,
        user_data={"username": test_user.username, "roles": ["user"]}
    )
    return sid
