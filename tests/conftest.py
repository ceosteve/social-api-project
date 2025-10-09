from turtle import title
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.main import app
from app import schemas
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models
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



#creating a test_user
@pytest.fixture
def test_user(client):
    user_data ={"email":"user2@gmail.com",
                "password":"user123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    print(res.json())
    new_user= res.json()
    new_user['password'] = user_data['password']
    return new_user



#another test_user
@pytest.fixture
def test_user2(client):
    user_data ={"email":"user12@gmail.com",
                "password":"user123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    print(res.json())
    new_user= res.json()
    new_user['password'] = user_data['password']
    return new_user


# this fixture will create a fake access token for us to use when testing since we are not running the api server
@pytest.fixture
def token(test_user):
    return create_access_token(data={"user_id":test_user['id']})


#taking original client and add the specific header that we get from the token fixture
@pytest.fixture
def authorized_client(client,token):
    client.headers = {
        **client.headers,
        "Authorization":f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [
        {"title":"first title",
        "content":"first content",
        "owner_id": test_user['id']},

        {"title":"2nd title",
        "content":"2nd content",
        "owner_id": test_user['id']},

        {"title":"3rd title",
        "content":"3rd content",
        "owner_id": test_user['id']},

        {"title":"3rd title",
        "content":"3rd content",
        "owner_id": test_user2['id']}
    ]


    def create_post_model(post):
        return models.Posts(**post)
    
    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    session.add_all(posts)
    #session.add_all([models.Posts(title="first title", content="first content", owner_id=test_user['id'])
    #                 models.User(title="2nd title", content="2nd content",owner_id=test_user['id']),
    #              models.User(title="3rd title", content="3rd content",owner_id=test_user['id'])])
    session.commit()

    posts =session.query(models.Posts).all()
    return posts

