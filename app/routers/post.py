
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

from app.cache import cache_get, cache_set


from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import Optional, List
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=['posts']
) 

# get all posts from the api server
@router.get("/", response_model=List[schemas.PostOut])
async def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""):
    
    cache_key = f"posts:{skip}:{limit}:{search or "all"}"

    cached_posts = await cache_get(cache_key)
    if cached_posts:
        return cached_posts
    
    results = db.query(
        models.Posts, func.count(models.Votes.post_id).label("votes")
    ).join(
        models.Votes, models.Votes.post_id == models.Posts.id, isouter=True
    ).group_by(
        models.Posts.id
    ).filter(
        models.Posts.content.contains(search)
    ).limit(limit).offset(skip).all()


    # transform each tuple into dict matching PostOut schema
    return [{"Post":post, "votes":vote} for post, vote in results]


 


# create a post in the api server
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=list[schemas.PostResponse]) 
def create_posts(posts: List[schemas.PostCreate], db:Session=Depends(get_db), current_user:int =Depends(oauth2.get_current_user)):

    new_posts=[models.Posts(owner_id=current_user.id,**post.dict()) for post in posts ]
    db.add_all(new_posts)
    db.commit()

    for post in new_posts:
        db.refresh(post)
    return new_posts 

 
#   get post by id
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
    
