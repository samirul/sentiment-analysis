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

    response = client.get("/all-categories", headers=headers)
    data = response.data.decode('utf-8')
    parsed_data = json.loads(data)
    assert 'id' in parsed_data["data"][0]
    assert 'category_name' in parsed_data["data"][0]
    assert 'user' in parsed_data["data"][0]
    assert parsed_data["data"][0].get('category_name') == 'category-xyz'
    assert parsed_data["data"][1].get('category_name') == 'category-abc'
    user.delete_one({"username": "cat1", "email": "cat1@cat.com"})
    category_db.delete_many({"user": user_info["_id"]})