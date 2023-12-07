from typing import Annotated
from fastapi import APIRouter, Depends
from app.database import get_db
from sqlalchemy.orm import Session
from app import database_models
from app import pydantic_models
from app import utils

router = APIRouter()

@router.get('/')
async def get_users(db: Annotated[Session, Depends(get_db)]):
    users_retrieved = db.query(database_models.Users).all()

    return users_retrieved

@router.post('/')
async def create_user(db: Annotated[Session, Depends(get_db)], user: pydantic_models.UserToCreate):

    new_user = database_models.Users()
    new_user.hashed_password = utils.hash(user.password)
    new_user.username = user.username

    db.add(new_user)
    db.commit()

    return {"message" : "successfully created the user"}