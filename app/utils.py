
import hashlib
from sys import prefix
from fastapi import Request
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto") #telling passlib what is the hashing algorithims


def hash(password:str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# function to generate cache keys from the request
def make_cache_key(request:Request, prefix:str="cache") -> str:

    path = request.url.path

    params = sorted(request.query_params.items())
    if params:
        param_string = "&".join(f"{k}={v}" for k, v in params)
    else:
        param_string = "no_params"
    
    hashed_key = hashlib.md5(param_string.encode()).hexdigest()

    return f"{path}:{hashed_key}"





