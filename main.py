from fastapi import FastAPI, Depends

import models
from company.dependencies import get_token_header
from database import engine
from routers import todos, auth, users, address
from company import companyapis

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Include auth router in app
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
app.include_router(address.router)

# Include company apis router in app, but determine prefixes from main instead of on company apis module
app.include_router(
    companyapis.router,
    prefix='/companyapis',
    tags=['companyapis'],
    dependencies=[Depends(get_token_header)],
    responses={418: {'description': 'internal use only'}}
)
