from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#databse connection string to be passed into SQLALCHEMY
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:postgres254@localhost/fastapi"
                        # specify that it is a psotgres database, give username, password, ip address and database name


#create an engine responsible for sqlalchemy to connect to a postgres database
engine=create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal=sessionmaker(autocommit=False,autoflush=False, bind=engine)

Base = declarative_base()


#creating a dependecy
#session object is responsible for creating a connection to the database
# function gets called everytime we get a request to the API endpoints created down below
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


