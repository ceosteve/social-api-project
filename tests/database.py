from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app
from app import schemas
from app.config import settings
from app.database import get_db, Base
from alembic import command

# creating a database connecton to the testing database which is different from our development database
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:postgres254@localhost:5432/fastapi_test"
#SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.database_username}:{
#    settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
                        # specify that it is a postgres database, give username, password, ip address and database name


#create an engine responsible for sqlalchemy to connect to a postgres database
engine=create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal=sessionmaker(autocommit=False,autoflush=False, bind=engine)


#create tables before running a test, running the test itself using the client defined and
# dropping the tables after test has been run
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine) 
    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


#create a test client and override connection to the dev database and return an instance of TestClient
@pytest.fixture()
def client(session):

    def overrideget_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db]=overrideget_db
    yield TestClient(app)

