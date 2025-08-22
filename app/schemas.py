
from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.database import Base



# specify the kind of data that the api server will accept from the user 
# not any other kind of data
# title str, content str,
# schema defined with pydantic model
 # inherit from the BaseModel class of pydantic module


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass



 #post response model
class PostResponse(PostBase):
    id: int
    created_at: datetime

    
    class Config:
      from_attributes = True


#schema to define the data a user provides when they send a request
# this is a pydantic model so it has to inherit from the BaseModel
class UserCreate(BaseModel):
    email: EmailStr
    password: str
   


# user response model, what data shoud users get back when they create an account
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        from_attributes = True  # convert from sqlalchemy model to a regular pydantic model


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    