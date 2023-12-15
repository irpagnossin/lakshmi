import pytest
from app.core import auth
from app.schemas.user import User


@pytest.fixture(scope="class")
def auth_obj():
    return auth


@pytest.fixture(scope="class")
def dummy_user() -> User:
    user = User(
        email="test@company.com",
        password=auth.hash_generator('123')
    )
    return User(**user.dict())
