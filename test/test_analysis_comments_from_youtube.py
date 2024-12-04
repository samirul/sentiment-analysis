from api import user
from api.tasks import task_celery_execute, Procressing
import json
import uuid
import pytest


def test_analysis_comments_from_youtube(client, get_access_token, set_user_info):
    access_token = get_access_token
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    
    # Send POST request
    response = client.post("/analysis-youtube-comments", headers=headers, json={"url": url})
 
    # Assert response
    assert response.status_code == 200
    assert 'msg' in response.json
    assert 'result_id' in response.json
    assert 'result_status' in response.json
    assert response.json['msg'] == 'Success'
    assert response.json['result_status'] == 'PENDING'
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_analysis_comments_from_youtube_failed_for_no_url(client, get_access_token, set_user_info):
    access_token = get_access_token
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    url = ""
    
    # Send POST request
    response = client.post("/analysis-youtube-comments", headers=headers, json={"url": url})
 
    # Assert response
    assert response.status_code == 404
    assert 'msg' in response.json
    assert 'result_id' not in response.json
    assert 'result_status' not in response.json
    assert response.json['msg'] == 'No url is found, add a url.'
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_analysis_comments_from_youtube_failed_for_no_access_token(client, get_access_token, set_user_info):
    url = ""
    # Send POST request
    response = client.post("/analysis-youtube-comments", json={"url": url})
    # Assert response
    assert response.status_code == 401
    assert 'error' in response.json
    assert 'result_id' not in response.json
    assert 'result_status' not in response.json
    assert response.json['error'] == 'Authorization header is missing or invalid'
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})
    

def test_celery_task_running(set_user_info):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    payload = {"user_id": str(user_id["_id"])}
    # payload = json.dumps(payload)
    assert task_celery_execute.delay(video_url=video_url, payload=payload, max_len=5).get() == "Done"
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_task_class_if_passed(set_user_info):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    payload = {"user_id": str(user_id["_id"])}
    process = Procressing(video_url=video_url, payload=payload, max_len=5)
    assert process.task() == "Done"
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_task_class_if_failed_wrong_type_id(set_user_info):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    payload = {"user_id": int(user_id["_id"])}
    process = Procressing(video_url=video_url, payload=payload, max_len=5)
    assert str(process.task()) == "'int' object has no attribute 'replace'"
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_task_if_no_url_being_send(set_user_info):
    user_id = set_user_info
    video_url = ""
    payload = {"user_id": int(user_id["_id"])}
    process = Procressing(video_url=video_url, payload=payload, max_len=5)
    assert str(process.task()) == "Video url isn't found, please add a url."
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_task_if_no_payload_being_send(set_user_info):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    payload = {}
    process = Procressing(video_url=video_url, payload=payload, max_len=5)
    assert str(process.task()) == "User is not logged in, not user information has been found."
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_task_if_no_max_len_being_send(set_user_info):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    payload = {"user_id": int(user_id["_id"])}
    process = Procressing(video_url=video_url, payload=payload, max_len=None)
    # print(process.task())
    assert str(process.task()) == "No max length is found."
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})
