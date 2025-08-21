from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils
from sqlalchemy.orm import Session
from ..database import get_db


router = APIRouter(
    prefix="/users"
)

#create users in the database
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut) # includes a status code to display that post has been created
def create_user(user: schemas.UserCreate, db:Session=Depends(get_db)):
    
    hashed_password= utils.hash(user.password) # hashing the password for security reasons
    user.password = hashed_password
    
    new_user = models.User(**user.dict()) # convert the user we get from our schema into a dict and unpack it
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# get user with specific id and not return the user's password
@router.get("/{id}",response_model=schemas.UserOut)
def get_user(id:int,db:Session=Depends(get_db)):
    user= db.query(models.User).filter(models.User.id==id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {id} does not exist")
    
    return user

@router.get("/users", response_model=schemas.UserOut)
def get_users(db:Session=Depends(get_db)):
    all_users=db.query(models.User).all()

    return all_users
    
