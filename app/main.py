from datetime import date, datetime
from gettext import find
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg
from psycopg.rows import dict_row
import time



app = FastAPI()


# specify the kind of data that the api server will accept from the user 
# not any other kind of data
# title str, content str,
# schema defined with pydantic model

class Post(BaseModel): # inherit from the BaseModel class of pydantic module
    title: str
    content: str
    published: bool = True

# block of code to connect to the database on the local machine 
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


# path operation is basically a decorator with a specific http method and a path
@app.get("/") # path operation (route)
def root(): # path operation functions (make them as descriptive as possible)
    return {"message": "welcome to my api@@"} #JSON language


# get all posts from the api server
@app.get("/posts")
def get_posts():
    cursor.execute("SELECT *FROM posts")
    posts =cursor.fetchall()
    return {"data":posts}


# create a post in the api server using the post HTTP method
@app.post("/posts", status_code=status.HTTP_201_CREATED) # includes a status code to display that post has been created
def create_posts(post: Post): # this is the pydantic model that was created earlier using the BaseModel class
    cursor.execute(
        "INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING *", 
        (post.title,post.content)
    )
    new_post = cursor.fetchone()
    conn.commit()

    return {"data":new_post} # kinda like JSON format of reading information from a database



# specify the status code that should be returned to the front end in case a resource
# is unavailable in the server
# data extracted is stored as a pydantic model and each has a method called .dict
# use best pratices and naming conventions 
@app.get("/posts/{id}") #id field represents a path parameter
def retrieve_post(id:int):
   cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
   post=cursor.fetchone()
   if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post with id :{id} was not found")
   return{"post detail":post}

# delete a post with a specific id
# status code 204 means that the request was successful but there is no content to return
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("DELETE FROM posts WHERE id=%s RETURNING *", (id,))
    delete_post= cursor.fetchone()
    conn.commit()

    if delete_post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)  
# No content to return after deletion

# update a post with a specific id
@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    cursor.execute("UPDATE posts SET title=%s, content=%s, published=%s RETURNING *",(post.title,post.content,post.published))

    updated_post=cursor.fetchone()
    if updated_post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")
    
    return {"data":updated_post}
    








