import uuid
import json
import pytest
from api import app, user, cache, category_db
from .random_object_id_generate.generate_id import random_object_id



@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def get_access_token():
    access_token = cache.get("test_user_key")
    token = access_token.decode().replace("'", '"')
    if token:
        return token
    return

@pytest.fixture
def get_user_info(get_access_token):
    user_info = cache.get("test_user_info")
    info = user_info.decode().replace("'", '"')
    if info:
        return info
    return

@pytest.fixture
def set_user_info(get_user_info):
    user_ = json.loads(get_user_info)
    id_ = uuid.UUID(user_.get("pk"))
    username = user_.get("email").split("@")[0]
    email = user_.get("email")
    inserted = user.insert_one({"_id": id_, "username": username, "email": email})
    user_detail = user.find_one({"_id": inserted.inserted_id})
    return user_detail


@pytest.fixture
def create_category(set_user_info):
    id_ = random_object_id()
    user_ = set_user_info
    custom_data ={
        "_id": id_,
        "category_name": "category-xyz",
        "user": user_["_id"]
    }
    check_data_already_in = category_db.find_one({"category_name": custom_data.get("category_name"),
                                                  "user": custom_data.get("user")
                                                  })
    if not check_data_already_in:
        category_id = category_db.insert_one(custom_data)
        return category_id.inserted_id


@pytest.fixture
def create_category2(set_user_info):
    id_ = random_object_id()
    user_ = set_user_info
    custom_data ={
        "_id": id_,
        "category_name": "category-abc",
        "user": user_["_id"]
    }
    check_data_already_in = category_db.find_one({"category_name": custom_data.get("category_name"),
                                                  "user": custom_data.get("user")
                                                  })
    if not check_data_already_in:
        category_id = category_db.insert_one(custom_data)
        return category_id.inserted_id

