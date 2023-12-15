from app.core.auth import hash_generator
from app.main import app
from fastapi import status
from fastapi.testclient import TestClient
from tests.app.auth.helpers import auth as endpoint
from tests.helpers import cleanup
from tests.helpers import database as db

client = TestClient(app)


user = {
    'email': 'teste@company.com.br',
    'password': hash_generator("123")
}


@cleanup(db)
def test_signin_with_correct_credentials():
    db.users.insert_one(user)

    form_user = {'username': user['email'], 'password': '123'}

    response = client.post(endpoint(), data=form_user)

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert 'access_token' in body
    assert 'token_type' in body
    assert body['token_type'] == 'bearer'


@cleanup(db)
def test_do_not_signin_with_incorrect_username():
    db.users.insert_one(user)

    form_user = {
        'username': 'incorrect_username@company.com.br',
        'password': '123'
    }

    response = client.post(endpoint(), data=form_user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@cleanup(db)
def test_do_not_signin_with_incorrect_password():
    db.users.insert_one(user)

    form_user = {'username': user['email'], 'password': '321'}

    response = client.post(endpoint(), data=form_user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@cleanup(db)
def test_do_not_signin_if_user_does_not_exist():

    form_user = {'username': user['email'], 'password': '123'}

    response = client.post(endpoint(), data=form_user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
