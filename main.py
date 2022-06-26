from fastapi import FastAPI, Depends
from starlette.staticfiles import StaticFiles

import models
from database import engine
from routers import todos, auth, users, address

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory='static'), name='static')

# Include auth router in app
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(address.router)
