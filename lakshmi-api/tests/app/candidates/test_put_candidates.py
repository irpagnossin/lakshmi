from datetime import datetime, timedelta

from app.schemas.candidate import Candidate
from tests.app.candidates.helpers import candidates as endpoint
from tests.helpers import cleanup, authorized
from tests.helpers import database as db
from tests.helpers import parse_datetime
from fastapi.testclient import TestClient
from app.main import app
from fastapi import status
import json

client = TestClient(app)


@cleanup(db)
def test_requires_authentication():
    candidate = Candidate(candidate_id='5', carreer_id=10, traits={'1': 100})
    db.candidates.insert_one(candidate.dict())

    response = client.put(
        endpoint(candidate.candidate_id), data=candidate.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@cleanup(db)
@authorized(db)
def test_put_uses_candidate_id(auth_headers):
    candidate = Candidate(candidate_id='5', carreer_id=10, traits={'1': 100})
    db.candidates.insert_one(candidate.dict())

    response = client.put(endpoint(candidate.candidate_id),
                          data=candidate.json(), headers=auth_headers)
    assert response.status_code == 200


@cleanup(db)
@authorized(db)
def test_created_at_is_read_only(auth_headers):
    candidate = Candidate(candidate_id='5', carreer_id=10, traits={'1': 100})
    db.candidates.insert_one(candidate.dict())

    created_at = db.candidates \
        .find_one({'candidate_id': candidate.candidate_id})['created_at']

    # Attempt to change created_at
    candidate.created_at = datetime.utcnow()

    response = client.put(endpoint(candidate.candidate_id),
                          data=candidate.json(), headers=auth_headers)
    updated_candidate = response.json()

    assert parse_datetime(updated_candidate['created_at']) == created_at


@cleanup(db)
@authorized(db)
def test_updated_at_is_read_only(auth_headers):
    yesterday = datetime.utcnow() - timedelta(days=1)
    tomorrow = datetime.utcnow() + timedelta(days=1)

    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 70, '2': 50}, updated_at=yesterday)
    db.candidates.insert_one(candidate.dict())

    candidate.updated_at = tomorrow

    response = client.put(endpoint(candidate.candidate_id),
                          data=candidate.json(), headers=auth_headers)
    updated_candidate = response.json()

    updated_at = parse_datetime(updated_candidate['updated_at'])
    assert yesterday < updated_at < tomorrow


@cleanup(db)
@authorized(db)
def test_dirty_is_read_only(auth_headers):
    candidate = Candidate(candidate_id='1', carreer_id=10,
                          traits={'1': 70, '2': 50})
    db.candidates.insert_one(candidate.dict())

    candidate.dirty = False

    response = client.put(endpoint(candidate.candidate_id),
                          data=candidate.json(), headers=auth_headers)
    updated_candidate = response.json()

    assert updated_candidate['dirty'] is True


@cleanup(db)
@authorized(db)
def test_candidate_id_read_only(auth_headers):
    candidate_id = 7
    candidate = Candidate(candidate_id=candidate_id, carreer_id=10,
                          traits={'1': 70, '2': 50})
    db.candidates.insert_one(candidate.dict())

    candidate.candidate_id = '999'

    response = client.put(endpoint(candidate_id),
                          data=candidate.json(), headers=auth_headers)
    assert response.status_code == 400


@cleanup(db)
@authorized(db)
def test_put_candidate_with_created_at_key(auth_headers):
    candidate_id = '7'
    created_at = datetime(2022, 8, 25, 12, 10)
    traits = {'1': 70, '2': 50}

    candidate = Candidate(created_at=created_at,
                          candidate_id=candidate_id,
                          carreer_id=10,
                          traits=traits)

    db.candidates.insert_one(candidate.dict())

    candidate.carreer_id = 20

    response = client.put(
        endpoint(candidate_id),
        data=json.dumps({'candidate_id': candidate.candidate_id,
                         'carreer_id': candidate.carreer_id,
                         'traits': traits}), headers=auth_headers)

    updated_candidate = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert updated_candidate['created_at'] == created_at.strftime(
        '%Y-%m-%dT%H:%M:%S')
