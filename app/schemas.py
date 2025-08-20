
from pydantic import BaseModel

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
