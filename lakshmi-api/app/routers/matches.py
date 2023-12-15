import os

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.auth import get_auth_user
from app.schemas.match import Match
from fastapi import APIRouter, Depends, HTTPException, status


collection = (
    AsyncIOMotorClient(os.environ["MONGODB_URL"])
    .get_default_database()
    .matches
)


router = APIRouter(
    dependencies=[Depends(get_auth_user)]
)


@router.get(
    "/positions/{position_id}/matches/",
    response_description="List matches",
    response_model=Match
)
async def list_matches(position_id: int, limit: int = 100, page: int = 1):
    """Lista os matches
    """
    # TODO: use separated documents to represent each candidate
    match = await collection.find_one({'position_id': position_id})

    if not match:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

    # TODO: do this in the database
    match['candidates'].sort(reverse=True, key=lambda c: c['score'])
    offset = (page-1)*limit
    match['candidates'] = match['candidates'][offset:offset+limit]

    return match
