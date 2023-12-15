from app.schemas.candidate import Candidate
from fastapi import status
from tests.app.candidates.helpers import candidates as endpoint
from tests.helpers import cleanup, authorized
from tests.helpers import database as db
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


@cleanup(db)
def test_requires_authentication():
    candidate_id = '999'
    response = client.delete(endpoint(candidate_id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@cleanup(db)
@authorized(db)
def test_delete_candidate_by_candidate_id(auth_headers):
    candidate = Candidate(candidate_id='15', carreer_id=10,
                          traits={'1': 100})
    db.candidates.insert_one(candidate.dict())

    response = client.delete(
        endpoint(candidate.candidate_id), headers=auth_headers)
    assert response.status_code == 204


@cleanup(db)
@authorized(db)
def test_returns_404(auth_headers):
    candidate_id = '999'
    response = client.delete(endpoint(candidate_id), headers=auth_headers)
    assert response.status_code == 404
