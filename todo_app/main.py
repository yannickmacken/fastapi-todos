from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from starlette import status

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


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


@app.get('/')
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@app.get('/{todo_id}')
async def read_todo(todo_id: int, db: Session = Depends(get_db)):

    # Query database for to do with same id, or raise exception
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@app.put('/{todo_id}', status_code=status.HTTP_201_CREATED)
async def update_todo(todo_id: int, todo: Todo, db: Session = Depends(get_db)):

    # Query database for to do with same id, or raise exception
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
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


@app.post('/', status_code=status.HTTP_201_CREATED)
async def create_todo(todo: Todo, db: Session = Depends(get_db)):

    # Build to do database model from to do model inputs
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    # Add to do database model to database
    db.add(todo_model)
    db.commit()
    return todo


@app.delete('/{todo_id}')
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):

    # Query database for to do with same id, or raise exception
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model:

        # Add to do model to database, overwriting previous model with same id
        db.delete(todo_model)
        db.commit()
        return f'deleted {todo_id}'

    raise HTTPException(status_code=404, detail="Todo not found")