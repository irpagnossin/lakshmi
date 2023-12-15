import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # TODO: isso não pode estar aqui1!!
    JWT_SECRET: str = os.environ['JWT_SECRET']
    """
    import secrets

    token: str = secrets.token_urlsafe(32)
    """
    ALGORITHM: str = 'HS256'
    # 1 ano
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 * 5 * 12

    @validator("BACKEND_CORS_ORIGINS", pre=True, allow_reuse=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> \
            Union[List[str], str]:

        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_HOST: str
    MYSQL_PORT: str
    MYSQL_DATABASE: str
    DATABASE_URI: Optional[str] = None

    @validator("DATABASE_URI", pre=True, allow_reuse=True)
    def assemble_db_connection(cls, v: Optional[str],
                               values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v

        return \
            f"mysql://{values.get('MYSQL_USER')}:" \
            f"{values.get('MYSQL_PASSWORD')}@{values.get('MYSQL_HOST')}:" \
            f"{values.get('MYSQL_PORT')}/{values.get('MYSQL_DATABASE')}"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
