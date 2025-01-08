import json
from api import sentiment_analysis_db, category_db, user



def test_all_comments_and_result(client, get_access_token, set_user_info, create_category, create_comments1, create_comments15, create_comments2):
    access_token = get_access_token
    user_info = set_user_info
    category_id = create_category
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = client.get(f"/all-youtube-comments-results/{category_id}/", headers=headers)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'id' in parsed_data['data'][0]
    assert 'id' in parsed_data['data'][1]
    assert 'video_title' in parsed_data['data'][0]
    assert parsed_data['data'][0]['video_title'] == 'xyz-title'
    assert 'video_title' in parsed_data['data'][1]
    assert parsed_data['data'][1]['video_title'] == 'xyz-title-15'
    assert 'video_url' in parsed_data['data'][0]
    assert parsed_data['data'][0]['video_url'] == 'xyz_url'
    assert 'video_url' in parsed_data['data'][1]
    assert parsed_data['data'][1]['video_url'] == 'xyz_url-15'
    assert 'comment' in parsed_data['data'][0]
    assert parsed_data['data'][0]['comment'] == 'xyz-comment'
    assert 'comment' in parsed_data['data'][1]
    assert parsed_data['data'][1]['comment'] == 'xyz-comment-15'
    assert 'main_result' in parsed_data['data'][0]
    assert parsed_data['data'][0]['main_result'] == 'xyz-main_result'
    assert 'main_result' in parsed_data['data'][1]
    assert parsed_data['data'][1]['main_result'] == 'xyz-main_result-15'
    assert 'other_result' in parsed_data['data'][0]
    assert parsed_data['data'][0]['other_result'] == 'xyz-other_result'
    assert 'other_result' in parsed_data['data'][1]
    assert parsed_data['data'][1]['other_result'] == 'xyz-other_result-15'
    assert 'user' in parsed_data['data'][0]
    assert 'user' in parsed_data['data'][1]
    assert 'category' in parsed_data['data'][0]
    assert 'category' in parsed_data['data'][1]
    assert response.status_code == 200
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_all_comments_and_result_failed_for_no_auth(client, get_access_token, set_user_info, create_category, create_comments1, create_comments15, create_comments2):
    user_info = set_user_info
    category_id = create_category
    response = client.get(f"/all-youtube-comments-results/{category_id}/")
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'data' not in parsed_data
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Authorization header is missing or invalid'
    assert response.status_code == 401
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_all_comments_and_result_failed_for_wrong_access_token(client, get_access_token, set_user_info, create_category, create_comments1, create_comments15, create_comments2):
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyQzdwIDPiPvv70yMzQ1Njc4OTDvv70sIm5hbWUiOiLKb3FPIEUvZSIsIu-_vWFOIjoxNT7vv70yMzkwM--_vX0.mUgFb0hxU8oqRjlC7Nxvp6dak5rULWHu9gnYvWHemoY'
    user_info = set_user_info
    category_id = create_category
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = client.get(f"/all-youtube-comments-results/{category_id}/", headers=headers)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'data' not in parsed_data
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Invalid token'
    assert response.status_code == 401
    sentiment_analysis_db.delete_many({"user": user_info["_id"]})
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})



