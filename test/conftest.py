import uuid
import json
import pytest
from bson.objectid import ObjectId
from api import app, user, cache, category_db, sentiment_analysis_db, celery_app
from .random_object_id_generate.generate_id import random_object_id



@pytest.fixture
def client():
    return app.test_client()

@pytest.fixture
def celery_app_test():
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield celery_app

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
    category_ids = []
    check_data_already_in = category_db.find_one({"category_name": custom_data.get("category_name"),
                                                  "user": custom_data.get("user")
                                                   })
    if not check_data_already_in:
        category_id = category_db.insert_one(custom_data)
        category_ids.append(category_id.inserted_id)
    else:
        category_ids.append(check_data_already_in['_id'])
    return category_ids[0]

@pytest.fixture
def create_category2(set_user_info):
    id_ = random_object_id()
    user_ = set_user_info
    custom_data ={
        "_id": id_,
        "category_name": "category-abc",
        "user": user_["_id"]
    }
    category_ids = []
    check_data_already_in = category_db.find_one({"category_name": custom_data.get("category_name"),
                                                  "user": custom_data.get("user")
                                                  })
    if not check_data_already_in:
        category_id = category_db.insert_one(custom_data)
        category_ids.append(category_id.inserted_id)
    else:
        category_ids.append(check_data_already_in['_id'])
    return category_ids[0]


    

@pytest.fixture
def create_comments1(set_user_info, create_category):
    id_ = random_object_id()
    user_ = set_user_info
    category_id = create_category
    custom_data ={
        "_id": id_,
        "video_title": "xyz-title",
        "video_url": "xyz_url",
        "comment": "xyz-comment",
        "main_result": "xyz-main_result",
        "other_result": "xyz-other_result",
        "user": user_["_id"],
        "category": ObjectId(category_id)

    }
    data = sentiment_analysis_db.insert_one(custom_data)
    return data.inserted_id

@pytest.fixture
def create_comments15(set_user_info, create_category):
    id_ = random_object_id()
    user_ = set_user_info
    category_id = create_category
    custom_data ={
        "_id": id_,
        "video_title": "xyz-title-15",
        "video_url": "xyz_url-15",
        "comment": "xyz-comment-15",
        "main_result": "xyz-main_result-15",
        "other_result": "xyz-other_result-15",
        "user": user_["_id"],
        "category": ObjectId(category_id)

    }
    data = sentiment_analysis_db.insert_one(custom_data)
    return data.inserted_id

@pytest.fixture
def create_comments2(set_user_info, create_category2):
    id_ = random_object_id()
    user_ = set_user_info
    category_id = create_category2
    custom_data ={
        "_id": id_,
        "video_title": "xyz-title_2",
        "video_url": "xyz_url_2",
        "comment": "xyz-comment_2",
        "main_result": "xyz-main_result_2",
        "other_result": "xyz-other_result_2",
        "user": user_["_id"],
        "category": ObjectId(category_id)

    }
    data = sentiment_analysis_db.insert_one(custom_data)
    return data.inserted_id


