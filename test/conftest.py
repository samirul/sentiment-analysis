import uuid
import pytest
from api import app, user, cache
import json


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


