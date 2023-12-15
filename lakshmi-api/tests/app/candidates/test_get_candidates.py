from app.main import app
from fastapi.testclient import TestClient
from tests.helpers import database as db
from tests.helpers import cleanup, authorized
from tests.app.candidates.helpers import candidates as endpoint
from app.schemas.candidate import Candidate
from datetime import datetime, timedelta
from fastapi import status


client = TestClient(app)


def common_scenario():
    first = datetime.now()
    second = first + timedelta(minutes=1)
    third = second + timedelta(minutes=1)

    candidates = [
        Candidate(candidate_id='1', carreer_id=10,
                  traits={'1': 70, '2': 50}, created_at=first),
        Candidate(candidate_id='2', carreer_id=20,
                  traits={'3': 90, '4': 30}, created_at=second),
        Candidate(candidate_id='3', carreer_id=20,
                  traits={'5': 1, '6': 2}, created_at=third)
    ]
    db.candidates.insert_many([c.dict() for c in candidates])


@cleanup(db)
def test_requires_authentication():
    response = client.get(endpoint())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@cleanup(db)
@authorized(db)
def test_get_without_parameters(auth_headers):
    common_scenario()

    response = client.get(endpoint(), headers=auth_headers)
    assert response.status_code == 200

    candidates = response.json()

    assert len(candidates) == 3

    assert candidates[0]['candidate_id'] == '3'
    assert candidates[0]['carreer_id'] == 20
    assert candidates[0]['traits'] == {'5': 1, '6': 2}

    assert candidates[1]['candidate_id'] == '2'
    assert candidates[1]['carreer_id'] == 20
    assert candidates[1]['traits'] == {'3': 90, '4': 30}

    assert candidates[2]['candidate_id'] == '1'
    assert candidates[2]['carreer_id'] == 10
    assert candidates[2]['traits'] == {'1': 70, '2': 50}


@cleanup(db)
@authorized(db)
def test_recent_candidates_first(auth_headers):
    common_scenario()

    response = client.get(endpoint(), headers=auth_headers)
    candidates = response.json()

    assert candidates[0]['created_at'] > candidates[1]['created_at']
    assert candidates[1]['created_at'] > candidates[2]['created_at']


@cleanup(db)
@authorized(db)
def test_get_limits(auth_headers):
    common_scenario()

    response = client.get(endpoint(), params={
                          'limit': 1}, headers=auth_headers)
    assert response.status_code == 200

    candidates = response.json()
    assert len(candidates) == 1


@cleanup(db)
@authorized(db)
def test_get_paginates(auth_headers):
    common_scenario()

    response = client.get(endpoint(), params={
                          'limit': 2, 'page': 2}, headers=auth_headers)
    assert response.status_code == 200

    candidates = response.json()
    assert len(candidates) == 1


@cleanup(db)
@authorized(db)
def test_get_candidate_by_external_id(auth_headers):
    common_scenario()

    candidate_id = '1'

    response = client.get(endpoint(candidate_id), headers=auth_headers)
    assert response.status_code == 200

    candidate = response.json()
    candidate['candidate_id'] == candidate_id
