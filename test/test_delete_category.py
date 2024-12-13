import json
from api import user, category_db

def test_delete_category(client, get_access_token, set_user_info, create_category):
    access_token = get_access_token
    user_info = set_user_info
    category_id = create_category
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = client.delete(f"/delete-category/{category_id}", headers=headers)
    assert response.status_code == 204
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})



def test_delete_category_failed_for_no_auth(client, get_access_token, set_user_info, create_category):
    user_info = set_user_info
    category_id = create_category
    response = client.delete(f"/delete-category/{category_id}")
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Authorization header is missing or invalid'
    assert response.status_code == 401
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})


def test_delete_category_failed_for_wrong_access_token(client, get_access_token, set_user_info, create_category):
    access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyQzdwIDPiPvv70yMzQ1Njc4OTDvv70sIm5hbWUiOiLKb3FPIEUvZSIsIu-_vWFOIjoxNT7vv70yMzkwM--_vX0.mUgFb0hxU8oqRjlC7Nxvp6dak5rULWHu9gnYvWHemoY'
    user_info = set_user_info
    category_id = create_category
    # Define headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = client.delete(f"/delete-category/{category_id}", headers=headers)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'error' in parsed_data
    assert parsed_data['error'] == 'Invalid token'
    assert response.status_code == 401
    category_db.delete_many({"user": user_info["_id"]})
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})