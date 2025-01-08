import json
from api import user, category_db


def test_category_if_created(client, get_access_token, set_user_info, create_category, create_category2):
    access_token = get_access_token
    user_info = set_user_info
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = client.get("/all-categories/", headers=headers)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'id' in parsed_data["data"][0]
    assert 'category_name' in parsed_data["data"][0]
    assert 'user' in parsed_data["data"][0]
    assert parsed_data["data"][0].get('category_name') == 'category-xyz'
    assert parsed_data["data"][1].get('category_name') == 'category-abc'
    assert response.status_code == 200
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})



def test_category_if_failed_to_get_without_auth(client, create_category, create_category2):
    response = client.get("/all-categories/", headers=None)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    print(parsed_data)
    assert 'data' not in parsed_data
    assert parsed_data['error'] == 'Authorization header is missing or invalid'
    assert response.status_code == 401
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_category_if_failed_for_wrong_access_token(client, get_access_token, set_user_info, create_category, create_category2):
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyQzdwIDPiPvv70yMzQ1Njc4OTDvv70sIm5hbWUiOiLKb3FPIEUvZSIsIu-_vWFOIjoxNT7vv70yMzkwM--_vX0.mUgFb0hxU8oqRjlC7Nxvp6dak5rULWHu9gnYvWHemoY'
    user_info = set_user_info
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = client.get("/all-categories/", headers=headers)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'data' not in parsed_data
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Invalid token'
    assert response.status_code == 401
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})
