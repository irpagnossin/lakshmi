from datetime import datetime, timedelta

from app.main import app
from app.schemas.position import JobPosition
from fastapi import status
from fastapi.testclient import TestClient
from tests.app.positions.helpers import positions as endpoint
from tests.helpers import authorized, cleanup
from tests.helpers import database as db

client = TestClient(app)


def common_scenario():
    t0 = datetime.now()

    boring_traits = {'11': [1, 3], '22': [2, 4]}
    boring_weights = {'11': 60, '22': 40}

    positions = [
        JobPosition(position_id=1, carreer_id=101, traits=boring_traits,
                    weights=boring_weights, created_at=t0 + timedelta(days=1)),
        JobPosition(position_id=2, carreer_id=102, traits=boring_traits,
                    weights=boring_weights, created_at=t0 + timedelta(days=2)),
        JobPosition(position_id=3, carreer_id=103, traits=boring_traits,
                    weights=boring_weights, created_at=t0 + timedelta(days=3)),
        JobPosition(position_id=4, carreer_id=104, traits=boring_traits,
                    weights=boring_weights, created_at=t0 + timedelta(days=4)),
        JobPosition(position_id=5, carreer_id=105, traits=boring_traits,
                    weights=boring_weights, created_at=t0 + timedelta(days=5))
    ]
    db.positions.insert_many([c.dict() for c in positions])


@cleanup(db)
def test_requires_authentication():
    common_scenario()

    position_id = 3

    response = client.get(endpoint(position_id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@cleanup(db)
@authorized(db)
def test_list_positions(auth_headers):
    common_scenario()

    response = client.get(endpoint(), headers=auth_headers)
    assert response.status_code == 200

    candidates = response.json()

    assert len(candidates) == 5

    assert candidates[0]['position_id'] == 5
    assert candidates[0]['carreer_id'] == 105

    assert candidates[1]['position_id'] == 4
    assert candidates[1]['carreer_id'] == 104

    assert candidates[2]['position_id'] == 3
    assert candidates[2]['carreer_id'] == 103

    assert candidates[3]['position_id'] == 2
    assert candidates[3]['carreer_id'] == 102

    assert candidates[4]['position_id'] == 1
    assert candidates[4]['carreer_id'] == 101


@cleanup(db)
@authorized(db)
def test_list_recent_positions_first(auth_headers):
    common_scenario()

    response = client.get(endpoint(), headers=auth_headers)
    positions = response.json()

    assert positions[0]['created_at'] > positions[1]['created_at']
    assert positions[1]['created_at'] > positions[2]['created_at']
    assert positions[2]['created_at'] > positions[3]['created_at']
    assert positions[3]['created_at'] > positions[4]['created_at']


@cleanup(db)
@authorized(db)
def test_list_positions_up_to_given_limit(auth_headers):
    common_scenario()

    response = client.get(endpoint(),
                          params={'limit': 3}, headers=auth_headers)

    positions = response.json()

    assert len(positions) == 3


@cleanup(db)
@authorized(db)
def test_paginate_positions(auth_headers):
    common_scenario()

    response = client.get(endpoint(), params={
                          'limit': 3, 'page': 2}, headers=auth_headers)

    positions = response.json()

    assert len(positions) == 2

    assert positions[0]['position_id'] == 2
    assert positions[0]['carreer_id'] == 102

    assert positions[1]['position_id'] == 1
    assert positions[1]['carreer_id'] == 101


@cleanup(db)
@authorized(db)
def test_get_position_by_external_id(auth_headers):
    common_scenario()

    position_id = 3

    response = client.get(endpoint(position_id), headers=auth_headers)
    assert response.status_code == 200

    candidate = response.json()
    candidate['position_id'] == position_id
