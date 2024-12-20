import os
import uuid
import json
from datetime import datetime, timedelta
import jwt
import pytest
from dotenv import load_dotenv
from bson.objectid import ObjectId
from api import app, user, category_db, sentiment_analysis_db, celery_app
from .random_object_id_generate.generate_id import random_object_id

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')

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
    access_token = jwt.encode({
        'user_id': str(uuid.uuid4()),
        'exp': datetime.utcnow() + timedelta(minutes=25)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return access_token

@pytest.fixture
def get_user_info(get_access_token):
    try:
        # Decode jwt token by using secret key
        access_token = get_access_token
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
        user_info = {"pk": payload['user_id'], 'email': 'cat1@cat.com'}
        return json.dumps(user_info)
    except jwt.ExpiredSignatureError:
        return f"token expired {401}"
    except jwt.InvalidTokenError:
        return f"token expired {401}"

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


