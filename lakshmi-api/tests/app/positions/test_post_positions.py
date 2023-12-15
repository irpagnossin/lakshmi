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
    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40}, dirty=False)

    response = client.post(
        endpoint(), data=position.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@cleanup(db)
@authorized(db)
def test_position_is_unique(auth_headers):
    # This position exists in the database
    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40})
    db.positions.insert_one(position.dict())

    # Now we try to PUT another position, having the same position_id
    position = JobPosition(position_id=11, carreer_id=102,
                           traits={'11': [1], '22': [2]},
                           weights={'11': 6, '22': 4})

    response = client.post(
        endpoint(), data=position.json(), headers=auth_headers)
    assert response.status_code == 400


@cleanup(db)
@authorized(db)
def test_created_at_is_read_only(auth_headers):
    yesterday = datetime.utcnow() - timedelta(days=1)

    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40}, created_at=yesterday)

    response = client.post(
        endpoint(), data=position.json(), headers=auth_headers)

    position = response.json()
    assert parse_datetime(position['created_at']) > yesterday


@cleanup(db)
@authorized(db)
def test_updated_at_is_read_only(auth_headers):
    yesterday = datetime.utcnow() - timedelta(days=1)

    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40}, updated_at=yesterday)

    response = client.post(
        endpoint(), data=position.json(), headers=auth_headers)

    position = response.json()
    assert position['updated_at'] is None


@cleanup(db)
@authorized(db)
def test_dirty_is_read_only(auth_headers):
    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40}, dirty=False)

    response = client.post(
        endpoint(), data=position.json(), headers=auth_headers)

    position = response.json()
    assert position['dirty'] is True
