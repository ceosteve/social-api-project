import atexit
from contextlib import asynccontextmanager
import logging
from xml.sax import handler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import post, user, auth, votes

from app.logging_config import setup_config
from app.logging_middleware import LoggingMiddleware



logger = setup_config()

for handlers in logger.handlers:
    handler.flush()


@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info("Application starting up")
    yield
    logger.info("Application shutting downs")

app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

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



@app.get("/")
def root(): 
    return {"message": "hello"} 


