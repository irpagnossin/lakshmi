import os
from unittest import mock
from jose import jwt
import jose
import pytest
from app.core.config import settings
from fastapi import HTTPException


@pytest.mark.usefixtures('dummy_user')
@pytest.mark.usefixtures('auth_obj')
class TestAuthenticate:

    @pytest.mark.asyncio
    async def test_unauthorized_if_token_is_invalid(self, auth_obj):
        with pytest.raises(HTTPException):
            await auth_obj.get_auth_user('invalid token')

    def test_verify_password(self, auth_obj):
        correct_password = '123'
        incorrect_password = '321'

        hashed_password = auth_obj.hash_generator(correct_password)

        is_verified = auth_obj.check_password(
            correct_password, hashed_password)

        assert is_verified

        is_verified = auth_obj.check_password(
            incorrect_password, hashed_password)

        assert not is_verified

    def test_create_valid_access_token(self, auth_obj, dummy_user):
        token = auth_obj.create_access_token(dummy_user.serialize())
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )

        user_email: str = payload.get("sub")

        assert isinstance(payload, dict)
        assert user_email == dummy_user.email

    @mock.patch.dict(os.environ, {"JWT_SECRET": "wrong_jwt_secret"})
    def test_try_create_access_token_with_wrong_secret_key(self, auth_obj,
                                                           dummy_user):
        token = auth_obj.create_access_token(dummy_user.serialize())
        JWT_SECRET: str = os.environ['JWT_SECRET']

        with pytest.raises(jose.exceptions.JWTError) as jwt_error:
            jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[settings.ALGORITHM],
                options={"verify_aud": False}
            )

        assert 'Signature verification failed' in str(jwt_error.value)
