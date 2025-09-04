from turtle import title
from typing import List
from app import schemas
import pytest



def test_get_all_posts(authorized_client, test_posts):
    result=authorized_client.get("/posts/")

    def post_out_model(post):
         return schemas.PostOut(**post)
    
    post_map= (map(post_out_model,result.json()))
    post_list= list(post_map)

    assert len(result.json())== len(test_posts)
    assert result.status_code == 200


def test_unauthorized_user_get_all_posts(client,test_posts):
     result= client.get("/posts/")
     assert result.status_code == 401


def test_unauthorized_user_get_one_posts(client,test_posts):
     result= client.get(f"/posts/{test_posts[0].id}")
     assert result.status_code == 401


def test_nonexistent_post(authorized_client,test_posts):
      result= authorized_client.get(f"/posts/55663")
      assert result.status_code == 404


def test_get_one_post(authorized_client,test_posts):
     result = authorized_client.get(f"/posts/{test_posts[0].id}")
     
     post = schemas.PostResponse(**result.json())
     assert result.status_code == 200
     assert post.id == test_posts[0].id
     assert post.content == test_posts[0].content


@pytest.mark.parametrize("title,content, published",[
     ("awesom title", "new content", True),
     ("next title", " next content", False),
     ("third title", " fourth content", True),
])


def test_create_post(authorized_client, test_user,title, content, published):
     result= authorized_client.post("/posts/", json={"title":title,
                                             "content":content, "published":published})
     created_post=schemas.PostResponse(**result.json())

     assert result.status_code == 201
     assert created_post.title == title
     assert created_post.content == content
     assert created_post.published == published
     assert created_post.owner_id == test_user['id']




def test_create_posts_default_published_true(authorized_client,test_user, test_posts):
     result= authorized_client.post("/posts/", json={"title":"new title",
                                             "content":"content new"})
     created_post=schemas.PostResponse(**result.json())
     assert result.status_code == 201
     assert created_post.title == "new title"
     assert created_post.content == "content new"
     assert created_post.published == True
     assert created_post.owner_id == test_user['id']



def test_unauthorized_user_create_posts(client,test_posts,test_user):
     result= client.post("/posts/", json={"title":"new title",
                                             "content":"content new"})
     assert result.status_code == 401



def test_unauthorized_user_delete_post(client,test_posts,test_user):
     result=client.delete(f"/posts/{test_posts[0].id}")
   
     assert result.status_code == 401



def test_delete_post(authorized_client,test_posts):
    result=authorized_client.delete(f"/posts/{test_posts[0].id}")

    assert result.status_code == 204



def test_delete_nonexstent_post(authorized_client,test_posts):
     result=authorized_client.delete("/posts/300")

     assert result.status_code ==404


def test_delete_post_not_owner(authorized_client,test_user,test_posts):
     result=authorized_client.delete(f"/posts/{test_posts[3].id}")
     assert result.status_code == 403

     

def test_update_post(authorized_client,test_user, test_posts):
     
     result=authorized_client.put(f"/posts/{test_posts[0].id}", json={"title":"new title",
                                             "content":"content new", "id":test_posts[0].id})
     updated_post = schemas.PostResponse(**result.json())
     
     assert result.status_code == 200
     assert updated_post.title == "new title"
     assert updated_post.content == "content new"


def test_update_post_not_owner(authorized_client, test_user, test_posts):
    result=authorized_client.put(f"/posts/{test_posts[3].id}", json={"title":"new title",
                                        "content":"content new", "id":test_posts[3].id})
    
    assert result.status_code == 403


def test_update_post_unauthorized_user(client, test_user, test_posts):
     result=client.put(f"/posts/{test_posts[1].id}")
     assert result.status_code == 401


def test_update_nonexstent_post(authorized_client,test_posts):
     result=authorized_client.put("/posts/300", json={"title":"new title",
                                        "content":"content new", "id":test_posts[3].id})

     assert result.status_code ==404

