
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import Optional, List
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=['posts']
)  # new instance that will be out path operations 

# get all posts from the api server
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    
   # posts = db.query(models.Posts).filter(
      #  models.Posts.content.contains(search)).limit(limit).offset(skip).all()
    
    
    results = db.query(
        models.Posts, func.count(models.Votes.post_id).label("votes")
    ).join(
        models.Votes, models.Votes.post_id == models.Posts.id, isouter=True
    ).group_by(
        models.Posts.id
    ).filter(
        models.Posts.content.contains(search)
    ).limit(limit).offset(skip).all()

    
  # if you want to access posts by a specific user

  #  posts=db.query(models.Posts).filter(
    #    models.Posts.owner_id==current_user.id)
    
#    cursor.execute("SELECT *FROM posts")
#    posts =cursor.fetchall()

    # transform each tuple into dict matching PostOut schema
    return [{"Post": post, "votes": votes} for post, votes in results]

 


# create a post in the api server using the post HTTP method
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse) # includes a status code to display that post has been created
def create_posts(post: schemas.PostCreate, db:Session=Depends(get_db), current_user:int =Depends(oauth2.get_current_user)): # this is the pydantic model that was created earlier using the BaseModel class
#    cursor.execute(
#        "INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING *", s
#        (post.title,post.content)
#    )
#    new_post = cursor.fetchone()
#    conn.commit()s
    new_post=models.Posts(owner_id=current_user.id,**post.dict())  #unpacked dictionary created under pydantic model
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post # kinda like JSON format of reading information from a database



 
# specify the status code that should be returned to the front end in case a resource
# is unavailable in the server
# data extracted is stored as a pydantic model and each has a method called .dict
# use best pratices and naming conventions 
@router.get("/{id}", response_model=schemas.PostResponse) #id field represents a path parameter
def retrieve_post(id:int,db:Session=Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):
#   cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))
#   post=cursor.fetchone()

    post= db.query(models.Posts).filter(models.Posts.id==id).first() # avoid going over all entries looking for id even if it has been found

    #results = db.query(models.Posts, func.count(models.Votes.post_id).label("Votes")).join(
       # models.Votes, models.Votes.post_id==models.Posts.id, isouter=True
       # ).group_by(models.Posts.id).filter(models.Posts.id==id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post with id :{id} was not found")
    
    # if you want to retrieve posts by a specific owner id
  #  if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    return post



# delete a post with a specific id
# status code 204 means that the request was successful but there is no content to return
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db:Session=Depends(get_db),current_user:int =Depends(oauth2.get_current_user)):

#    cursor.execute("DELETE FROM posts WHERE id=%s RETURNING *", (id,))
#    delete_post= cursor.fetchone()
#    conn.commit()

    post_query=db.query(models.Posts).filter(models.Posts.id==id)
   
    post = post_query.first()

    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)  
# No content to return after deletion




# update a post with a specific id
@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, post: schemas.PostCreate, db:Session=Depends(get_db),current_user:int =Depends(oauth2.get_current_user)):

#    cursor.execute("UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *",(post.title,post.content,post.published, (id,)))

#    updated_post=cursor.fetchone()
#    conn.commit() # save changes permanently to the database
    
     post_query = db.query(models.Posts).filter(models.Posts.id == id)

     updated_post = post_query.first()

     if updated_post is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} not found"
        )

     if updated_post.owner_id != current_user.id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )

    # ✅ Use dict() from the Pydantic schema
     post_query.update(post.dict(), synchronize_session=False)
     db.commit()

     return post_query.first()  # for postman 
    
