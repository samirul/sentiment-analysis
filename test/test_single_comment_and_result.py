import json
from bson.objectid import ObjectId
from api import user, category_db, sentiment_analysis_db

def test_single_comment_and_result(client, get_access_token, set_user_info, create_category, create_comments1, create_comments2):
    access_token = get_access_token
    user_info = set_user_info
    comment1 = create_comments1
    category_id = create_category
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.get(f"/get-youtube-comment-result/{comment1}", headers=headers)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'data' in parsed_data
    assert 'id' in parsed_data['data'][0]
    assert 'video_title' in parsed_data['data'][0]
    assert 'video_url' in parsed_data['data'][0]
    assert 'comment' in parsed_data['data'][0]
    assert 'main_result' in parsed_data['data'][0]
    assert 'other_result' in parsed_data['data'][0]
    assert 'user' in parsed_data['data'][0]
    assert parsed_data['data'][0]['video_title'] == 'xyz-title'
    assert parsed_data['data'][0]['video_url'] == 'xyz_url'
    assert parsed_data['data'][0]['comment'] == 'xyz-comment'
    assert parsed_data['data'][0]['main_result'] == 'xyz-main_result'
    assert parsed_data['data'][0]['other_result'] == 'xyz-other_result'
    assert parsed_data['data'][0]['user'] == str(user_info["_id"])
    assert parsed_data['data'][0]['category'] == str(category_id)
    assert response.status_code == 200
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_single_comment_and_result_if_auth_is_not_provided(client, get_access_token, set_user_info, create_category, create_comments1, create_comments2):
    access_token = get_access_token
    user_info = set_user_info
    comment1 = create_comments1
    category_id = create_category
    response = client.get(f"/get-youtube-comment-result/{comment1}")
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'data' not in parsed_data
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Authorization header is missing or invalid'
    assert response.status_code == 401
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_single_comment_and_result_if_wrong_auth_token_provided(client, get_access_token, set_user_info, create_category, create_comments1, create_comments2):
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyQzdwIDPiPvv70yMzQ1Njc4OTDvv70sIm5hbWUiOiLKb3FPIEUvZSIsIu-_vWFOIjoxNT7vv70yMzkwM--_vX0.mUgFb0hxU8oqRjlC7Nxvp6dak5rULWHu9gnYvWHemoY'
    user_info = set_user_info
    comment1 = create_comments1
    category_id = create_category
     # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = client.get(f"/get-youtube-comment-result/{comment1}", headers=headers)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'data' not in parsed_data
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Invalid token'
    assert response.status_code == 401
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})
