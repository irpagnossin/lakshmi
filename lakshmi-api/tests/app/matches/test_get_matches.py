from app.schemas.match import Match
from fastapi import status
from tests.app.matches.helpers import matches as endpoint
from tests.helpers import cleanup, authorized
from tests.helpers import database as db
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


@cleanup(db)
def test_requires_authentication():
    position_id = 2
    response = client.get(endpoint(position_id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def common_scenario():
    matches = [
        Match(position_id=1, candidates=[
            {'candidate_id': '1', 'score': 11},
            {'candidate_id': '2', 'score': 22},
            {'candidate_id': '3', 'score': 33},
            {'candidate_id': '4', 'score': 44},
            {'candidate_id': '5', 'score': 55},
            {'candidate_id': '6', 'score': 66}
        ]),
        Match(position_id=2, candidates=[
            {'candidate_id': '13', 'score': 35},
            {'candidate_id': '14', 'score': 45},
            {'candidate_id': '15', 'score': 55}
        ])
    ]
    db.matches.insert_many([m.dict() for m in matches])


@cleanup(db)
@authorized(db)
def test_get_matches_by_position_id(auth_headers):
    common_scenario()

    position_id = 2

    response = client.get(endpoint(position_id), headers=auth_headers)
    assert response.status_code == 200

    match = response.json()
    assert match['position_id'] == position_id


@cleanup(db)
@authorized(db)
def test_higher_scores_first(auth_headers):
    common_scenario()

    position_id = 2

    response = client.get(endpoint(position_id), headers=auth_headers)
    match = response.json()
    candidates = match['candidates']

    assert len(candidates) == 3

    assert candidates[0]['candidate_id'] == '15'
    assert candidates[0]['score'] == 55

    assert candidates[1]['candidate_id'] == '14'
    assert candidates[1]['score'] == 45

    assert candidates[2]['candidate_id'] == '13'
    assert candidates[2]['score'] == 35


@cleanup(db)
@authorized(db)
def test_get_respect_limit(auth_headers):
    common_scenario()

    position_id = 2

    response = client.get(endpoint(position_id), params={
                          'limit': 2}, headers=auth_headers)
    assert response.status_code == 200

    match = response.json()
    candidates = match['candidates']
    assert len(candidates) == 2


@cleanup(db)
@authorized(db)
def test_get_paginates(auth_headers):
    common_scenario()

    position_id = 1

    response = client.get(endpoint(position_id),
                          params={'limit': 4, 'page': 2}, headers=auth_headers)
    assert response.status_code == 200

    match = response.json()
    candidates = match['candidates']
    assert len(candidates) == 2

    assert candidates[0]['candidate_id'] == '2'
    assert candidates[0]['score'] == 22

    assert candidates[1]['candidate_id'] == '1'
    assert candidates[1]['score'] == 11


@cleanup(db)
@authorized(db)
def test_return_204_when_requested_position_does_not_exist(auth_headers):

    position_id = 99999

    response = client.get(endpoint(position_id), headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
