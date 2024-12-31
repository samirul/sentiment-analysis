import time
from api.tasks import task_run


def test_task_status_running(client, get_access_token, set_user_info, celery_app_test):
    user_id = set_user_info
    video_url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    payload = {"user_id": str(user_id["_id"])}
    task = task_run.delay(video_url=video_url, payload=payload, max_len=5)  # Provide valid arguments
    task_id = task.id

    headers = {
        "Authorization": f"Bearer {get_access_token}",
        "Content-Type": "application/json",
    }
    response = client.get(f'/task_status/{task_id}/', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['state'] == 'RUNNING'
    assert data['progress'] == 100


def test_task_status_failure(client, get_access_token, set_user_info, celery_app_test):
    user_id = set_user_info
    video_url = ""
    payload = {"user_id": str(user_id["_id"])}
    task = task_run.delay(video_url=video_url, payload=payload, max_len=5)
    task_id = task.id


    while not task.ready():
        time.sleep(1)

    headers = {
        "Authorization": f"Bearer {get_access_token}",
        "Content-Type": "application/json",
    }

    response = client.get(f'/task_status/{task_id}/', headers=headers)
    data = response.get_json()

    assert response.status_code == 200
    assert data['state'] == 'PENDING'
    assert data['progress'] == 0


def test_task_status_check_auth_fail(client, get_access_token, set_user_info, celery_app_test):
    user_id = set_user_info
    video_url = ""
    payload = {"user_id": str(user_id["_id"])}
    task = task_run.delay(video_url=video_url, payload=payload, max_len=5)
    task_id = task.id

    response = client.get(f'/task_status/{task_id}/')
    data = response.get_json()

    assert response.status_code == 401
    assert data['error'] == 'Authorization header is missing or invalid'