import http
import logging
from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from.. database import get_db
from .. import schemas, models, utils, oauth2

logger =logging.getLogger("socialapi")

router = APIRouter(
    tags=['authentication']
)


@router.post("/login", response_model=schemas.Token)
def login(user_credentials:OAuth2PasswordRequestForm= Depends(), db: Session=Depends(get_db)):

    user= db.query(models.User).filter(models.User.email==user_credentials.username).first()
   
    if not user:
        logger.warning("user tried logging in with invalid credentials")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    
    if not utils.verify(user_credentials.password, user.password):
         logger.warning("user tried logging in with invalid credentials")
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    
    access_token= oauth2.create_access_token(data={"user_id":user.id})

    logger.info(f"user with id {user.id} logged in")
    return{"access_token":access_token, "token_type":"bearer"}

# creating authentication tokens
# creating user login end point to acesss the API



    
    