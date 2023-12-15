import os
from datetime import datetime, timedelta

import motor.motor_asyncio
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pytz import timezone

collection = (
    motor
    .motor_asyncio
    .AsyncIOMotorClient(os.environ["MONGODB_URL"])
    .get_default_database()
    .users
)


CRIPTO = CryptContext(schemes=['bcrypt'], deprecated='auto')


def check_password(password: str, password_hash: str) -> bool:
    """
    Função para verificar se a senha está correta, comparando
    a senha em texto puro informada pelo usuário, e o hash da
    senha que estará salvo no banco de dados durante a criação
    da conta.
    """
    return CRIPTO.verify(password, password_hash)


def hash_generator(password: str) -> str:
    """
    Função que gera e retorna o hash da senha
    """
    return CRIPTO.hash(password)


def _create_token_payload(token_type: str, ttl: timedelta, sub: str) -> str:
    # https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.3

    utc = timezone('utc')

    expire = datetime.now(tz=utc) + ttl

    payload = {
        'type': token_type,
        'exp': expire,
        'iat': datetime.now(tz=utc),
        'sub': sub
    }

    return jwt.encode(payload, settings.JWT_SECRET,
                      algorithm=settings.ALGORITHM)


def create_access_token(sub: str) -> str:
    """
    https://jwt.io
    """
    return _create_token_payload(
        token_type='access_token',
        ttl=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        sub=sub
    )


oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/signin"
)


async def get_auth_user(token: str = Depends(oauth2_schema)) -> bool:
    credential_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Unable to authenticate credential.',
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )
        user_email: str = payload.get("sub")

        if user_email is None:
            raise credential_exception

    except JWTError:
        raise credential_exception

    user = await collection.find_one({'email': user_email})

    if user is None:
        raise credential_exception
