from api import user, category_db, sentiment_analysis_db
from api.tasks import task_run

def test_analysis_comments_from_youtube(client, celery_app_test, get_access_token, set_user_info):
    access_token = get_access_token
    user_info = set_user_info
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    max_len = 5
    
    # Send POST request
    response = client.post("/analysis-youtube-comments/", headers=headers, json={"url": url, "max_len": max_len})
 
    # Assert response
    assert response.status_code == 200
    assert 'msg' in response.json
    assert 'result_id' in response.json
    assert 'result_status' in response.json
    assert response.json['msg'] == 'Success'
    assert response.json['result_status'] == 'SUCCESS'
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_analysis_comments_from_youtube_failed_for_wrong_access_token(client, celery_app_test, get_access_token, set_user_info):
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyQzdwIDPiPvv70yMzQ1Njc4OTDvv70sIm5hbWUiOiLKb3FPIEUvZSIsIu-_vWFOIjoxNT7vv70yMzkwM--_vX0.mUgFb0hxU8oqRjlC7Nxvp6dak5rULWHu9gnYvWHemoY'
    user_info = set_user_info
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    max_len = 5
    
    # Send POST request
    response = client.post("/analysis-youtube-comments/", headers=headers, json={"url": url, "max_len": max_len})
 
    # Assert response
    assert 'msg' not in response.json
    assert 'result_id' not in response.json
    assert 'result_status' not in response.json
    assert 'error' in response.json
    assert response.json['error'] == 'Invalid token'
    assert response.status_code == 401
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_analysis_comments_from_youtube_failed_for_no_url(client, celery_app_test, get_access_token, set_user_info):
    access_token = get_access_token
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    url = ""
    max_len = 5
    
    # Send POST request
    response = client.post("/analysis-youtube-comments/", headers=headers, json={"url": url, "max_len": max_len})
 
    # Assert response
    assert response.status_code == 404
    assert 'msg' in response.json
    assert 'result_id' not in response.json
    assert 'result_status' not in response.json
    assert response.json['msg'] == 'No url is found, add a url.'
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_analysis_comments_from_youtube_failed_for_no_access_token(client, celery_app_test, get_access_token, set_user_info):
    url = ""
    max_len = 5
    # Send POST request
    response = client.post("/analysis-youtube-comments/", json={"url": url, "max_len": max_len})
    # Assert response
    assert response.status_code == 401
    assert 'error' in response.json
    assert 'result_id' not in response.json
    assert 'result_status' not in response.json
    assert response.json['error'] == 'Authorization header is missing or invalid'
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})
    

def test_celery_task_running(set_user_info, celery_app_test):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    payload = {"user_id": str(user_id["_id"])}
    assert str(task_run.delay(video_url=video_url, payload=payload, max_len=5).get()) == "{'current': 5, 'total': 5, 'status': 'Task completed!'}"
    sentiment_analysis_db.delete_many({"user": user_id["_id"]})
    category_db.delete_many({"user": user_id["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_celery_task_failed_no_url(set_user_info, celery_app_test):
    user_id = set_user_info
    video_url = ""
    payload = {"user_id": str(user_id["_id"])}
    assert str(task_run.delay(video_url=video_url, payload=payload, max_len=5).get()) == "Video url isn't found, please add a url."
    sentiment_analysis_db.delete_many({"user": user_id["_id"]})
    category_db.delete_many({"user": user_id["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})

def test_celery_task_failed_no_auth(set_user_info, celery_app_test):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    assert str(task_run.delay(video_url=video_url, payload=None, max_len=5).get()) == "User is not logged in, not user information has been found."
    sentiment_analysis_db.delete_many({"user": user_id["_id"]})
    category_db.delete_many({"user": user_id["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})

def test_celery_task_failed_no_max_len(set_user_info, celery_app_test):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    payload = {"user_id": str(user_id["_id"])}
    assert str(task_run.delay(video_url=video_url, payload=payload, max_len=None).get()) == "No max length is found."
    sentiment_analysis_db.delete_many({"user": user_id["_id"]})
    category_db.delete_many({"user": user_id["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})

def test_celery_task_failed_wrong_type_id(set_user_info, celery_app_test):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    payload = {"user_id": int(user_id["_id"])}
    assert str(task_run.delay(video_url=video_url, payload=payload, max_len=5).get()) == "'int' object has no attribute 'replace'"
    sentiment_analysis_db.delete_many({"user": user_id["_id"]})
    category_db.delete_many({"user": user_id["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


