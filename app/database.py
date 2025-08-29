from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg
from psycopg.rows import dict_row
import time
from .config import settings


#database connection string to be passed into SQLALCHEMY
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.database_username}:{
    settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
                        # specify that it is a postgres database, give username, password, ip address and database name


#create an engine responsible for sqlalchemy to connect to a postgres database
engine=create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False,autoflush=False, bind=engine)

Base = declarative_base() #class for from which SQLALCHEMY models inherit


#creating a dependecy
#session object is responsible for creating a connection to the database
# function gets called everytime we get a request to the API endpoints created down below
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()



    
