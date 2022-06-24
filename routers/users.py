from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi import Depends, HTTPException, APIRouter

import models
from database import engine, SessionLocal
from routers.auth import get_current_user, get_user_exception, verify_password, \
    get_password_hash

router = APIRouter(prefix='/users', tags=['users'], responses={404: {'description': 'Not found'}})

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


@router.get('/')
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Users).all()


@router.get('/{user_id}')
async def read_user(user_id: int, db: Session = Depends(get_db)):

    # Query database for to do with same id, or raise exception
    user_model = db.query(models.Users) \
        .filter(models.Users.id == user_id).first()
    if user_model:
        return user_model
    raise HTTPException(status_code=404, detail="User not found")


@router.get('/user/')
async def read_user(user_id: int, db: Session = Depends(get_db)):

    # Query database for to do with same id, or raise exception
    user_model = db.query(models.Users) \
        .filter(models.Users.id == user_id).first()
    if user_model:
        return user_model
    raise HTTPException(status_code=404, detail="User not found")


@router.put('/user/password')
async def user_password_change(
        user_verification: UserVerification,
        user: dict = Depends(get_current_user),  # Returns username and id from JWT
        db: Session = Depends(get_db)):

    # If invalid JWT, raise error
    if not user:
        raise get_user_exception()

    # Find current user in database
    user_model = db.query(models.Users).filter(models.Users.id == user.get('id')).first()

    # Perform an extra user password check
    if user_model:
        if user_verification.username == user_model.username and verify_password(
                user_verification.password,
                user_model.hashed_password):

            # Save user with new password to database
            user_model.hashed_password = get_password_hash(user_verification.new_password)
            db.add(user_model)
            db.commit()
            return 'Succesful'

    return 'Invalid user or request'


@router.delete('/user')
async def delete_user(user: dict = Depends(get_current_user),  # Returns username and id from JWT
                      db: Session = Depends(get_db)):

    # If invalid JWT, raise error
    if not user:
        raise get_user_exception()

    # Find current user in database
    user_model = db.query(models.Users).filter(models.Users.id == user.get('id')).first()

    if user_model:
        db.delete(user_model)
        db.commit()
        return 'Delete successful'

    return 'Delete failed'




