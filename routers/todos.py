from typing import Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from fastapi import Depends, HTTPException, APIRouter, Request
from starlette import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


import models
from database import engine, SessionLocal
from routers.auth import get_current_user, get_user_exception

router = APIRouter(prefix='/todos', tags=['todos'], responses={404: {'description': 'Not found'}})

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):  # Model to determine the post request valid inputs, not for the database model
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description='Priority must be between 1-5')
    complete: bool


@router.get('/test')
async def test(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get('/')
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@router.get('/user')
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()


@router.get('/{todo_id}')
async def read_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    # Query database for to do with same id, or raise exception
    todo_model = db.query(models.Todos) \
        .filter(models.Todos.id == todo_id) \
        .filter(models.Todos.owner_id == user.get('id')) \
        .first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.put('/{todo_id}', status_code=status.HTTP_201_CREATED)
async def update_todo(todo_id: int, todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    # Query database for to do with same id, or raise exception
    todo_model = db.query(models.Todos) \
        .filter(models.Todos.id == todo_id) \
        .filter(models.Todos.owner_id == user.get('id')) \
        .first()
    if todo_model:

        # Overwrite to do model attributes
        todo_model.title = todo.title
        todo_model.description = todo.description
        todo_model.priority = todo.priority
        todo_model.complete = todo.complete

        # Add to do model to database, overwriting previous model with same id
        db.add(todo_model)
        db.commit()
        return todo

    raise HTTPException(status_code=404, detail="Todo not found")


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    # Build to do database model from to do model inputs
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get('id')

    # Add to do database model to database
    db.add(todo_model)
    db.commit()
    return todo


@router.delete('/{todo_id}')
async def delete_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):

    # Query database for to do with same id, or raise exception
    todo_model = db.query(models.Todos) \
        .filter(models.Todos.id == todo_id) \
        .filter(models.Todos.owner_id == user.get('id')) \
        .first()
    if todo_model:

        # Add to do model to database, overwriting previous model with same id
        db.delete(todo_model)
        db.commit()
        return f'deleted {todo_id}'

    raise HTTPException(status_code=404, detail="Todo not found")