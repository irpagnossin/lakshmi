from datetime import datetime, timedelta
from app.schemas.candidate import Candidate
from tests.app.candidates.helpers import candidates as endpoint
from tests.helpers import cleanup, authorized
from tests.helpers import database as db
from tests.helpers import parse_datetime
from fastapi.testclient import TestClient
from app.main import app
from fastapi import status


client = TestClient(app)


@cleanup(db)
def test_requires_authentication():
    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 70, '2': 50}, dirty=False)

    response = client.post(
        endpoint(), data=candidate.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@cleanup(db)
@authorized(db)
def test_candidate_is_unique(auth_headers):
    # This candidate exists in the database
    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 70, '2': 50})
    db.candidates.insert_one(candidate.dict())

    # This is a new one, but with same candidate_id
    another_candidate = Candidate(candidate_id='1', carreer_id=7,
                                  traits={'88': 1, '89': 100})

    response = client.post(
        endpoint(), data=another_candidate.json(), headers=auth_headers)
    assert response.status_code == 400


@cleanup(db)
@authorized(db)
def test_created_at_is_read_only(auth_headers):
    yesterday = datetime.now() - timedelta(days=1)
    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 70, '2': 50}, created_at=yesterday)

    response = client.post(
        endpoint(), data=candidate.json(), headers=auth_headers)
    inserted_candidate = response.json()
    assert parse_datetime(inserted_candidate['created_at']) > yesterday


@cleanup(db)
@authorized(db)
def test_updated_at_is_read_only(auth_headers):
    yesterday = datetime.now() - timedelta(days=1)

    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 70, '2': 50}, updated_at=yesterday)

    response = client.post(
        endpoint(), data=candidate.json(), headers=auth_headers)

    candidate = response.json()
    assert candidate['updated_at'] is None


@cleanup(db)
@authorized(db)
def test_dirty_is_read_only(auth_headers):
    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 70, '2': 50}, dirty=False)

    response = client.post(
        endpoint(), data=candidate.json(), headers=auth_headers)

    candidate = response.json()
    assert candidate['dirty'] is True
