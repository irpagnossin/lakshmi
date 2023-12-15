from datetime import datetime, timedelta

from app.schemas.position import JobPosition
from tests.app.positions.helpers import positions as endpoint
from tests.helpers import cleanup, authorized
from tests.helpers import database as db
from tests.helpers import parse_datetime
from fastapi.testclient import TestClient
from app.main import app
from fastapi import status


client = TestClient(app)


@cleanup(db)
def test_requires_authentication():
    position_id = 7
    position = JobPosition(position_id=position_id, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40})
    db.positions.insert_one(position.dict())
    position.position_id = 999

    response = client.put(endpoint(position_id),
                          data=position.json())

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@cleanup(db)
@authorized(db)
def test_put_uses_position_id(auth_headers):
    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40})
    db.positions.insert_one(position.dict())

    response = client.put(endpoint(position.position_id),
                          data=position.json(),  headers=auth_headers)
    assert response.status_code == 200


@cleanup(db)
@authorized(db)
def test_created_at_is_read_only(auth_headers):
    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40})
    db.positions.insert_one(position.dict())

    created_at = db.positions \
        .find_one({'position_id': position.position_id})['created_at']

    # Attempt to change created_at
    position.created_at = datetime.now()

    response = client.put(endpoint(position.position_id),
                          data=position.json(), headers=auth_headers)
    updated_position = response.json()

    assert parse_datetime(updated_position['created_at']) == created_at


@cleanup(db)
@authorized(db)
def test_updated_at_is_read_only(auth_headers):
    yesterday = datetime.utcnow() - timedelta(days=1)
    tomorrow = datetime.utcnow() + timedelta(days=1)

    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40}, updated_at=yesterday)
    db.positions.insert_one(position.dict())

    position.carreer_id = 102
    position.updated_at = tomorrow

    response = client.put(endpoint(position.position_id),
                          data=position.json(), headers=auth_headers)
    updated_position = response.json()

    updated_at = parse_datetime(updated_position['updated_at'])
    assert updated_position['carreer_id'] == position.carreer_id
    assert yesterday < updated_at < tomorrow


@cleanup(db)
@authorized(db)
def test_dirty_is_read_only(auth_headers):
    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40})
    db.positions.insert_one(position.dict())

    position.carreer_id = 102
    position.dirty = False

    response = client.put(endpoint(position.position_id),
                          data=position.json(), headers=auth_headers)
    updated_position = response.json()

    assert updated_position['carreer_id'] == position.carreer_id
    assert updated_position['dirty'] is True


@cleanup(db)
@authorized(db)
def test_set_dirty_to_true(auth_headers):
    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40}, dirty=False)
    db.positions.insert_one(position.dict())

    position.carreer_id = 103

    response = client.put(endpoint(position.position_id),
                          data=position.json(), headers=auth_headers)
    updated_position = response.json()

    assert updated_position['carreer_id'] == position.carreer_id
    assert updated_position['dirty'] is True


@cleanup(db)
@authorized(db)
def test_position_id_read_only(auth_headers):
    position_id = 7
    position = JobPosition(position_id=position_id, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40})
    db.positions.insert_one(position.dict())
    position.position_id = 999

    response = client.put(endpoint(position_id),
                          data=position.json(), headers=auth_headers)
    assert response.status_code == 400
