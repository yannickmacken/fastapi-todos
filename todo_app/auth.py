from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models
from database import engine, SessionLocal


# Determine secret key and algorithm type used to decode information in Json Web Token
SECRET_KEY = "aD3d2f32432oI293j5i2k26lJ343"
ALGORITHM = "HS256"


class CreateUser(BaseModel):
    """Request model to create and update user."""
    username: str
    email: Optional[str]
    first_name: str
    last_name: str
    password: str


# Create crypt context to hash and verify password
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Initialize app
app = FastAPI()

# Create database with schema or if database schema is existing, update schema in database
models.Base.metadata.create_all(bind=engine)

# Used to decode Json Web Token
oath2_bearer = OAuth2PasswordBearer(tokenUrl='token')


def get_db():
    """Method to start a new session to access the database."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post('/create/user')
async def create_new_user(create_user: CreateUser, db: Session = Depends(get_db)):

    # Build user database model from user model input
    create_user_model = models.Users()
    create_user_model.email = create_user.email
    create_user_model.username = create_user.username
    create_user_model.first_name = create_user.first_name
    create_user_model.last_name = create_user.last_name
    hash_password = get_password_hash(create_user.password)
    create_user_model.hashed_password = hash_password
    create_user_model.is_active = True

    # Add user database model to database
    db.add(create_user_model)
    db.commit()

    return create_user


@app.post('/token')
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise get_user_exception()
    token_expires = timedelta(minutes=20)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)
    return token


async def get_current_user(token: str = Depends(oath2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=404, detail='User not found')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise get_user_exception()


# Exceptions
def get_user_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate':'Bearer'},
    )