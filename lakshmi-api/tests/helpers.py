import os
from datetime import datetime

from app.core.auth import create_access_token, hash_generator
from app.schemas.user import User
from pymongo import MongoClient


def cleanup(database):
    def decorator(f):
        def wrapper():
            database.candidates.drop()
            database.matches.drop()
            database.positions.drop()
            database.users.drop()
            f()

        return wrapper
    return decorator


def parse_datetime(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')


def user_authentication_headers(database):
    user = User(user_id=1, email='teste@company.com.br',
                password=hash_generator('123'), created_at=datetime.utcnow())

    database.users.insert_one(user.dict())
    auth_token = create_access_token(user.serialize())

    return {"Authorization": f"Bearer {auth_token}"}


def authorized(database):
    def authorized_with_database(f):
        def wrapper():
            auth_headers = user_authentication_headers(database)
            f(auth_headers)
        return wrapper
    return authorized_with_database


database = MongoClient(os.environ["MONGODB_URL"]).get_default_database()
