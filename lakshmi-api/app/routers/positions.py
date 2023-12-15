import os
from datetime import datetime
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from app.core.auth import get_auth_user
from app.schemas.position import JobPosition, UpdateJobPosition
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


collection = (
    AsyncIOMotorClient(os.environ["MONGODB_URL"])
    .get_default_database()
    .positions
)


router = APIRouter(
    dependencies=[Depends(get_auth_user)]
)


@router.get(
    "/positions/",
    response_description="List all job positions",
    response_model=List[JobPosition]
)
async def list_positions(limit: int = 100, page: int = 1):
    """Lista as vagas de trabalho
    """

    # TODO: assert limit and page > 0

    positions = await collection \
        .find() \
        .limit(limit) \
        .sort('created_at', pymongo.DESCENDING) \
        .skip((page-1)*limit) \
        .to_list(limit)

    return positions


@router.get(
    "/positions/{position_id}",
    response_description="Get a single job position",
    response_model=JobPosition
)
async def show_position(position_id: int):
    position = await collection.find_one({"position_id": position_id})
    if position is not None:
        return position

    raise HTTPException(status_code=404,
                        detail=f"Position {position_id} not found")


@router.post(
    "/positions/",
    response_description="Add new job position",
    response_model=JobPosition
)
async def create_position(position: JobPosition = Body(...)):

    existing = await collection.find_one({
        'position_id': position.position_id
    })

    if existing is not None:  # TODO: set position_id as primary key
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'msg': 'Position already exists. Use PUT.'}
        )

    # TODO: what is a better way to do this?
    position.created_at = datetime.utcnow()
    position.updated_at = None
    position.dirty = True

    position = jsonable_encoder(position)

    new_position = await collection.insert_one(position)
    created_position = await collection.find_one({
        "_id": new_position.inserted_id
    })

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created_position
    )


# TODO: find a better way to ignore user inputs for created_at, updated_at
# and dirty
@router.put(
    "/positions/{position_id}",
    response_description="Update a job position",
    response_model=JobPosition
)
async def update_position(position_id: int,
                          position: UpdateJobPosition = Body(...)):

    if not position_id == position.position_id:
        raise HTTPException(status_code=400, detail="Cannot edit candidate_id")

    position = {
        k: v for k, v in position.dict(exclude_unset=True).items()
        if v is not None
    }

    if 'created_at' in position:
        del position['created_at']

    if len(position) >= 1:
        # TODO: what is a better way to do this?
        position['dirty'] = True
        position['updated_at'] = datetime.utcnow()

        update_result = await collection.update_one(
            {"position_id": position_id},
            {"$set": position}
        )

        if update_result.modified_count == 1:
            updated_position = \
                await collection.find_one({"position_id": position_id})

            if updated_position is not None:
                return updated_position

    existing_position = await collection.find_one({"position_id": position_id})
    if existing_position is not None:
        return existing_position

    raise HTTPException(status_code=404,
                        detail=f"Job position {position_id} not found")


@router.delete(
    "/positions/{position_id}",
    response_description="Delete a job position"
)
async def delete_position(position_id: int):
    delete_result = await collection.delete_one({"position_id": position_id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404,
                        detail=f"Job position {position_id} not found")
