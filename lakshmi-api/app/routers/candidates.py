import os
from datetime import datetime
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from app.core.auth import get_auth_user
from app.schemas.candidate import Candidate, UpdateCandidate
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


collection = (
    AsyncIOMotorClient(os.environ["MONGODB_URL"])
    .get_default_database()
    .candidates
)

router = APIRouter(
    dependencies=[Depends(get_auth_user)]
)


@router.get(
    "/candidates/",
    response_description="List all candidates",
    response_model=List[Candidate]
)
async def list_candidates(limit: int = 100, page: int = 1):
    """Lista os candidatos

    Os candidatos são ex-alunos que acumularam habilidades e
    competências suficientes para candidatarem-se a vagas de trabalho
    na carreira escolhida.
    """

    candidates = await collection \
        .find() \
        .limit(limit) \
        .sort('created_at', pymongo.DESCENDING) \
        .skip((page-1)*limit) \
        .to_list(limit)

    return candidates


# TODO: require token for all requests
@router.get(
    "/candidates/{candidate_id}",
    response_description="Get a single candidate",
    response_model=Candidate
)
async def show_candidate(candidate_id: str):
    candidate = await collection.find_one({'candidate_id': candidate_id})
    if candidate is not None:
        return candidate

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Candidate {candidate_id} not found")


@router.post(
    "/candidates/",
    response_description="Add new candidate",
    response_model=Candidate
)
async def create_candidate(candidate: Candidate = Body(...)):

    existing = await collection.find_one({
        'candidate_id': candidate.candidate_id
    })

    if existing is not None:  # TODO: set candidate_id as primary key
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'msg': 'Candidate already exists. Use PUT.'}
        )

    # TODO: what is a better way to do this?
    candidate.created_at = datetime.utcnow()
    candidate.updated_at = None
    candidate.dirty = True

    candidate = jsonable_encoder(candidate)

    new_candidate = await collection.insert_one(candidate)
    created_candidate = await collection.find_one({
        "_id": new_candidate.inserted_id
    })

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created_candidate
    )


@router.put(
    "/candidates/{candidate_id}",
    response_description="Update a candidate",
    response_model=Candidate
)
async def update_candidate(candidate_id: str,
                           candidate: UpdateCandidate = Body(...)):

    if not candidate_id == candidate.candidate_id:
        raise HTTPException(status_code=400, detail="Cannot edit candidate_id")

    candidate = {
        k: v for k, v in candidate.dict(exclude_unset=True).items()
        if v is not None
    }

    if 'created_at' in candidate:
        del candidate['created_at']

    if len(candidate) >= 1:
        # TODO: what is a better way to do this?
        candidate['dirty'] = True
        candidate['updated_at'] = datetime.utcnow()

        update_result = await collection.update_one(
            {"candidate_id": candidate_id},
            {"$set": candidate}
        )

        if update_result.modified_count == 1:
            updated_candidate = \
                await collection.find_one({"candidate_id": candidate_id})

            if updated_candidate is not None:
                return updated_candidate

    existing_candidate = \
        await collection.find_one({"candidate_id": candidate_id})

    if existing_candidate is not None:
        return existing_candidate

    raise HTTPException(status_code=404,
                        detail=f"Candidate {candidate_id} not found")


@router.delete(
    "/candidates/{candidate_id}",
    response_description="Delete a candidate"
)
async def delete_candidate(candidate_id: str):
    delete_result = await collection.delete_one({"candidate_id": candidate_id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404,
                        detail=f"Candidate {candidate_id} not found")
