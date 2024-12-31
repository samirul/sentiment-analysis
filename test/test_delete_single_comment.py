import json
from api import user, sentiment_analysis_db, category_db


def test_delete_single(client, get_access_token, set_user_info, create_category, create_comments1, create_comments15, create_comments2):
    access_token = get_access_token
    user_info = set_user_info
    comment_15_id = create_comments15
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = client.delete(f"/delete-comment/{comment_15_id}/", headers=headers)
    assert response.status_code == 204
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_delete_single_failed_for_no_auth(client, get_access_token, set_user_info, create_category, create_comments1, create_comments15, create_comments2):
    user_info = set_user_info
    comment_15_id = create_comments15
    response = client.delete(f"/delete-comment/{comment_15_id}/")
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Authorization header is missing or invalid'
    assert response.status_code == 401
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_delete_single_failed_for_wrong_access_token(client, get_access_token, set_user_info, create_category, create_comments1, create_comments15, create_comments2):
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyQzdwIDPiPvv70yMzQ1Njc4OTDvv70sIm5hbWUiOiLKb3FPIEUvZSIsIu-_vWFOIjoxNT7vv70yMzkwM--_vX0.mUgFb0hxU8oqRjlC7Nxvp6dak5rULWHu9gnYvWHemoY'
    user_info = set_user_info
    comment_15_id = create_comments15
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.delete(f"/delete-comment/{comment_15_id}/", headers=headers)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Invalid token'
    assert response.status_code == 401
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})