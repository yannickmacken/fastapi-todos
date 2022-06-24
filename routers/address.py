from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import Depends, HTTPException, APIRouter
from starlette import status

import models
from database import engine, SessionLocal
from routers.auth import get_current_user, get_user_exception


router = APIRouter(
    prefix="/address",
    tags=["address"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Address(BaseModel):
    address1: str
    address2: Optional[str]
    apt_num: Optional[str]
    city: str
    state: str
    country: str
    postalcode: str


@router.post("/")
async def create_address(address: Address, user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()

    address_model = models.Address()
    address_model.address1 = address.address1
    address_model.address2 = address.address2
    address_model.apt_num = address.apt_num
    address_model.city = address.city
    address_model.state = address.state
    address_model.country = address.country
    address_model.postalcode = address.postalcode

    db.add(address_model)
    db.flush()  # This kind of half commits the address model to database, an id is created for the address

    # Add the address id to the current logged in user
    user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    user_model.address_id = address_model.id

    db.add(user_model)
    db.commit()


