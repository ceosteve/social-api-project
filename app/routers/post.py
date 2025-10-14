
import hashlib
from fastapi import FastAPI, Request, Response, status, HTTPException, Depends, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime
from app.cache import cache_clear_pattern, cache_get, cache_set
from app.utils import make_cache_key
import json

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
    request:Request,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""):
    
    cache_key = make_cache_key(request)

    cached_posts = await cache_get(cache_key)

    if cached_posts:
        body = json.dumps(cached_posts,sort_keys=True)
        etag = hashlib.md5(body.encode()).hexdigest()
        last_modified = datetime.utcnow().strftime("%a, %d %m %Y %H:%M:%S GMT")
        
        if request.headers.get("if-none-match")==etag:
            return Response(status_code=304)
        
        response = JSONResponse(content=cached_posts)
        response.headers["X-Cache"] = "HIT"
        response.headers["Cache-Control"] = "public, max-age=60"
        response.headers["ETag"] = etag
        response.headers["Last-Modified"] = last_modified

        return response
    
    results = db.query(
        models.Posts, func.count(models.Votes.post_id).label("votes")
    ).join(
        models.Votes, models.Votes.post_id == models.Posts.id, isouter=True
    ).group_by(
        models.Posts.id
    ).filter(
        models.Posts.content.contains(search)
    ).limit(limit).offset(skip).all()

    posts = [
        {"Post":post, "votes":vote} for post, vote in results
    ]

    serialized_posts = jsonable_encoder(posts)

    await cache_set(cache_key, serialized_posts, expire=120)
    
    # compute the etag and last modified headers
    body = json.dumps(serialized_posts, sort_keys=True)
    etag = hashlib.md5(body.encode()).hexdigest()
    last_modified = datetime.utcnow().strftime("%a, %d %m %Y %H:%M:%S GMT")

    # format the response headers
    response = JSONResponse(content=serialized_posts)
    response.headers['X-Cache'] = "MISS"
    response.headers["Cache-Control"] = "public, max-age-60"
    response.headers ["ETag"] = etag
    response.headers["Last-Modified"] = last_modified

    
    return response


 

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
@router.get("/{id}", response_model=schemas.PostResponse)
def retrieve_post(id:int,db:Session=Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):


    post= db.query(models.Posts).filter(models.Posts.id==id).first()

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
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db:Session=Depends(get_db),current_user:int =Depends(oauth2.get_current_user)):


    post_query=db.query(models.Posts).filter(models.Posts.id==id)
   
    post = post_query.first()

    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"post with id {id} not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this action")
    
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)  





# update a post with a specific id
@router.put("/{id}", response_model=schemas.PostResponse)
async def update_post(id: int, post: schemas.PostCreate, db:Session=Depends(get_db),current_user:int =Depends(oauth2.get_current_user)):

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

     await cache_clear_pattern("cache:/posts")
     return post_query.first()  
    
