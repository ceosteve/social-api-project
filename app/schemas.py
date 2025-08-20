
from datetime import datetime
from pydantic import BaseModel



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

 
class PostResponse(PostBase):
    id: int
    created_at: datetime

    
    class Config:
      from_attributes = True