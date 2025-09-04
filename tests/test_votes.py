import json
from unittest import result
import pytest
from app import models



@pytest.fixture
def test_vote(session, test_user, test_posts):
    new_vote =models.Votes(post_id=test_posts[2].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()




def test_vote_on_post(authorized_client, test_posts):
    result=authorized_client.post("/vote/", json={"post_id":test_posts[0].id, "dir":1})

    assert result.status_code == 201



def test_vote_on_already_voted_post(authorized_client, test_posts, test_vote):
    result=authorized_client.post("/vote/",json={"post_id":test_posts[2].id, "dir":1})

    assert result.status_code == 409



def test_delete_vote(authorized_client, test_posts, test_vote):
    result=authorized_client.post("/vote/", json={"post_id":test_posts[2].id, "dir":0})

    assert result.status_code == 201



def test_delete_nonexistent_vote(authorized_client, test_posts):
    result=authorized_client.post("/vote/",json={"post_id":test_posts[2].id, "dir":0})
    
    assert result.status_code == 404


def test_vote_post_nonexsist(authorized_client, test_posts):
    result=authorized_client.post("/vote/",json={"post_id":8000, "dir":1})

    assert result.status_code == 404

def test_unauthorized_user_vote(client, test_posts):
    result=client.post("/vote/",json={"post_id":test_posts[2].id, "dir":1})

    assert result.status_code == 401

    
