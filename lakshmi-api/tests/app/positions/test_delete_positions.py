from app.main import app
from app.schemas.position import JobPosition
from fastapi.testclient import TestClient
from tests.app.positions.helpers import positions as endpoint
from tests.helpers import authorized, cleanup
from tests.helpers import database as db
from fastapi import status

client = TestClient(app)


@cleanup(db)
def test_requires_authentication():
    position_id = 999
    response = client.delete(endpoint(position_id))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@cleanup(db)
@authorized(db)
def test_delete_position_by_position_id(auth_headers):
    position = JobPosition(position_id=11, carreer_id=101,
                           traits={'11': [1, 3], '22': [2, 4]},
                           weights={'11': 60, '22': 40})
    db.positions.insert_one(position.dict())

    response = client.delete(endpoint(position.position_id),
                             headers=auth_headers)
    assert response.status_code == 204


@cleanup(db)
@authorized(db)
def test_returns_404(auth_headers):
    position_id = 999
    response = client.delete(endpoint(position_id), headers=auth_headers)
    assert response.status_code == 404
