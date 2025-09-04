from app import schemas
from jose import jwt
from app.config import settings
import pytest




def test_root(client):
    res =client.get("/")
    print(res.json().get('message'))
    assert (res.json().get('message')) == 'hello'
    assert res.status_code == 200


def test_create_user(client):
    res = client.post("/users/", json={"email":"user2@gmail.com","password":"user123"})
    
    new_user=schemas.UserOut(**res.json())
    assert new_user.email== "user2@gmail.com"
    assert res.status_code==201


def test_login_user(client, test_user):
     res = client.post("/login", data={"username":test_user['email'],"password":test_user['password']})
     login_res=schemas.Token(**res.json())
     payload = jwt.decode(login_res.access_token, settings.secret_key, settings.algorithm)
     id = payload.get("user_id")
     assert id == test_user['id']
     assert login_res.token_type == "bearer"
     assert res.status_code ==200



@pytest.mark.parametrize("email, password, status_code", [
    ("worongemail@gmail.com", "user123", 403),
    ("user2@gmail.com", "user222", 403),
    (None, "user123", 403),
    ("user2@gmail.com", None, 403),
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})

    assert res.status_code == status_code
    if status_code == 403:  # only check detail for invalid credentials
        assert res.json().get('detail') == "Invalid credentials"




