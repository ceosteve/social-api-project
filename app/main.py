
from fastapi import FastAPI

from . import models
from .database import engine
from .routers import post, user, auth
from .config import settings


models.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

# path operation is basically a decorator with a specific http method and a path
@app.get("/") # path operation (route)
def root(): # path operation functions (make them as descriptive as possible)
    return {"message": "welcome to my api@@"} #JSON language




