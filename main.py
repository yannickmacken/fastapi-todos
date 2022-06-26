from fastapi import FastAPI, Depends

import models
from database import engine
from routers import todos, auth, users, address

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Include auth router in app
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(address.router)
