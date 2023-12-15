import os
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.auth import check_password, create_access_token, hash_generator
from app.schemas.user import User
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm


db = AsyncIOMotorClient(os.environ["MONGODB_URL"]).get_default_database()
collection = db.users

router = APIRouter()


@router.post("/signup")
async def signup(user: User = Body(...)):

    existing = await collection.find_one({
        'email': user.email
    })

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User already exists'
        )

    user.password = hash_generator(user.password)
    user.created_at = datetime.utcnow()
    user.updated_at = None

    user = jsonable_encoder(user)
    new_user = await collection.insert_one(user)

    created_user = await collection.find_one({
        "_id": new_user.inserted_id
    })

    del created_user['password']

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created_user
    )


@router.post("/signin")
async def signin(form_data: OAuth2PasswordRequestForm = Depends()):

    user = await User.find(db, email=form_data.username)

    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password.")

    if not check_password(form_data.password, user.password):
        raise HTTPException(
            status_code=400, detail="Incorrect username or password.")

    return JSONResponse(
        content={"access_token": create_access_token(user.serialize()),
                 "token_type": "bearer"}, status_code=status.HTTP_200_OK)
