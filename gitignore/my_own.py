import http
import sys

import sqlalchemy

from app import oauth2
from app.database import SQLALCHEMY_DATABASE_URL, SessionLocal
from gitignore import my_own
print("Python executable in use:", sys.executable)

try:
    import fastapi
    print("FastAPI is installed at:", fastapi.__file__)
except ImportError:
    print("FastAPI is NOT installed in this environment")


from operator import index
from random import randrange
from turtle import pos
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, status, HTTPException, Depends, Response, APIRouter
import psycopg
from psycopg.rows import dict_row
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from app import schemas, models, utils
from sqlalchemy import Column, String, Boolean, CHAR, Integer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from ..app.oauth2 import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

app = FastAPI()

router = APIRouter()
class Post(BaseModel):
    title: str
    content: str
    rating:Optional[int] = None


while True:
    try:
        conn= psycopg.connect(
            dbname="fastapi", 
            user="postgres", 
            password="postgres254",
            host="localhost")

        cursor = conn.cursor(row_factory=dict_row) # return each row of data as a dictionary with column titles as keys
        print("database connection successful")
        break

    except Exception as error:
        print("database connection failed")
        print("error is:", error)
        time.sleep(5)


all_posts=[{"title":"post 1 title", "content":"content of post 1", "id":1},
            {"title":"post 2 title", "content":"conttent of post 2", "id":2}
            ]


def find_posts(id):
    for i,p in enumerate(all_posts):
        if p['id'] == id:
            return p
        

@app.get("/")
def root():
    return {"message":"welcome to my api server"}


@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")  # SQL query to extract all data from the database and return it in the form of a dictionary
    posts=cursor.fetchall()

    return{"data":posts}

@app.get("/post/{id}")
def get_post(id:int):
    cursor.execute("SELECT * FROM posts WHERE id=%s", (id,))
    post=cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post with id :{id} was not found")
    return{f"posts":post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post:Post):
    cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING *", 
                   (post.title, post.content,))
    new_post = cursor.fetchone()
    conn.commit() # persistence in the database

    return{f"post created":new_post}



@app.put("posts/{id}")
def update_post(id:int, post:Post):
    cursor.execute("UPDATE posts SET title=%s, content=%s WHERE id=%s RETURNING*",(post.title, post.content,(id,)))
    updated_post = cursor.fetchone()
    conn.commit()
    
    if updated_post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

    return {"updated posts":updated_post}



@app.delete("/posts/{id}")
def delete_post(id:int):
    cursor.execute("DELETE FROM posts WHERE id=%s RETURNING*",(id,))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)  



# defining how the database will be set up using SQLALCHEMY

SQLALCHEMY_DATABASE_URL = "postgres+psycopg://postgres:postgres@254localhost/fastapi"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoconnect=False, autoflush=False, bind=engine)


Base= declarative_base()


def get_db():
    db= SessionLocal
    try:
        yield db
    finally:
        db.close()



#creating database models using sqlalchemy
class Pets(Base):
    __tablename__= "current pets"

    name = Column("name",String,nullable=False)
    color = Column("color", String, nullable=False)
    number = Column("number", Integer, nullable = False)


#path operation function
@app.get("/pets",status_code=status.HTTP_200_OK)
def get_posts(db:Session= Depends(get_post)):
    pets=db.query(Pets).all()
    return{"data": pets}



#path operation to create new user in the database
@app.post("/users",status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate, db:Session=Depends(get_db)):
    new_user=models.User(user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



# end point to create a jwt token by the api
def create_token(data:dict):
    to_encode=data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt_token =jwt.encode(to_encode,SECRET_KEY,ALGORITHM)

    return encoded_jwt_token


# endpoint to login and get a jwt access token from the api
@router.post("/login")
def login(user_credentials: schemas.UserLogin, db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.email==user_credentials.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"invalid login details")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"invalid login credentials")
    
    access_token = oauth2.create_access_token(data={"user_id":user.id})
    
    return access_token


# function to verfy that the jwt token created at the point of login is valid 