from datetime import date, datetime
from gettext import find
from signal import raise_signal
from urllib.parse import uses_relative
from warnings import deprecated
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from typing import Optional, List
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user, auth


models.Base.metadata.create_all(bind=engine)



app = FastAPI()



# block of code to connect to the database on the local machine using SQL
while True:
    try:  
        conn = psycopg.connect("dbname=fastapi user=postgres password=postgres254 host=localhost")
       
        cursor= conn.cursor(row_factory=dict_row) # to execute SQL statements
        print("Database connection successful")
        break

    except Exception as error:
        print("Database connection failed")
        print("error", error)
        time.sleep(3)
    



my_posts = [ 
    {"title":"title of post 1","content":"content of post 1", "id":1},
    {"title":"favorite foods","content":"I like pizza", "id":2}

]



def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p




# helper function to find the index of a post by its id
# this is useful for deleting a post
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id']==id:
            return i



app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

# path operation is basically a decorator with a specific http method and a path
@app.get("/") # path operation (route)
def root(): # path operation functions (make them as descriptive as possible)
    return {"message": "welcome to my api@@"} #JSON language




