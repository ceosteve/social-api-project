from email import header
import secrets
from tarfile import data_filter
from xml.dom import minicompat
from jose import jwt, JWTError
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session


# this is like a helper function to get the JWT token from the header of a request and validate it
oauth2_scheme = OAuth2PasswordBearer("login")




# this handles the logic of creating JWT tokens
# secret key
# algorithm we want to use
# expiration time of the token

SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data:dict):
    to_encode=data.copy()

    expire= datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,ALGORITHM)

    return encoded_jwt


#def verify_access_token(token:str, credentials_exception):
    
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id:str=payload.get("user_id")

        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData()
    except JWTError:
        raise credentials_exception
    
    return token_data



def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
