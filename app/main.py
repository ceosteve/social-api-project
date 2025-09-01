
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import post, user, auth, votes
from .config import settings


# no longer need this command since we have alembic which is handling the creation of sqlalchemy models in our database
#models.Base.metadata.create_all(bind=engine)


app = FastAPI()

# allowing requests from sepcific domains to talk to our api
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(votes.router)

# path operation is basically a decorator with a specific http method and a path
@app.get("/") # path operation (route)
def root(): # path operation functions (make them as descriptive as possible)
    return {"message": "hello"} #JSON language



