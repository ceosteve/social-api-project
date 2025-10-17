# this is a special class (BaseSettings) that automatically loads values from environment variables like .env files into python attributes
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expiration_time: int
    redis_host:str
    redis_port:str

    class Config:
        env_file = ".env" # load a file names .env from the project directory

settings = Settings()
