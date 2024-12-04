""" 
    Here route act as endpoint for link
    and for writing certain logics.

"""
import uuid
import json
from collections import OrderedDict
from bson.objectid import ObjectId
from flask import request, jsonify, Response
from api import app, sentiment_analysis_db, cache, category_db
from api.tasks import task_celery_execute
from api.producers import RabbitMQConnection
from jwt_token.jwt_token_verify import jwt_login_required

rabbit_mq = RabbitMQConnection()

@app.route("/analysis-youtube-comments", methods=["POST"])
@jwt_login_required
def analysis_comments_from_youtube(payload):
    """Responsible for executing celery task sentiment analysis. 

    Returns:
        Response: This function execute celery taks and provide
        task ID and response type - [POST] and status code - 200 OK
        with json format else return status code - 400 bad request.
    """
    try:
        inputed_text = request.json.get("url")
        if not inputed_text:
            response_data = json.dumps({"msg": "No url is found, add a url."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        result = task_celery_execute.delay(video_url=inputed_text, payload=payload, max_len=5)
        return jsonify({"msg": "Success", "result_id": result.id, "result_status": result.status}),200
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')
    

    
@app.route("/all-youtube-comments-results/<category_id>", methods=['GET'])
@jwt_login_required
def get_all_comments_and_results(payload, category_id):
    """Get all the data from MongoDB database.

    Args:
        payload (UUID): Get user_id from payload after authentication. 

    Returns:
        return: Return all the data (200) from mongodb by searching user_id and category_id else
        return no data found (404) or something wrong happened exception or bad
        request (400).
    """
    try:
        # check if cached response avaliable or not
        cached_item = cache.get(f"sentiment_analysis_all_data_{payload['user_id']}_{category_id}")
        if cached_item:
            deserialized_data = json.loads(cached_item)
            response_data = json.dumps(deserialized_data, indent=4)
            return Response(response_data, status=200, mimetype='application/json')

        data = []
        comments = sentiment_analysis_db.find({"user": uuid.UUID(payload['user_id']), "category": ObjectId(category_id)})
        if sentiment_analysis_db.count_documents({}) == 0:
            response_data = json.dumps({"msg": "data is not found."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        for comment in comments:
            print(comments)
            dict_items = OrderedDict([
                ("id", str(comment["_id"])),
                ("video_title", str(comment["video_title"])),
                ("video_url", str(comment["video_url"])),
                ("comment", str(comment["comment"])),
                ("main_result", str(comment["main_result"])),
                ("other_result", str(comment["other_result"])),
                ("user", str(comment["user"])),
                ("category", str(comment["category"])),
            ])  
            data.append(dict_items)
        response_data = json.dumps({"data": data}, indent=4)
        cache.set(f"sentiment_analysis_all_data_{payload['user_id']}_{category_id}", response_data)
        return Response(response_data, status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')


@app.route("/get-youtube-comment-result/<ids>", methods=["GET"])
@jwt_login_required
def get_single_comment_and_result(ids, payload):
    """Get single data from MongoDB database.

    Args:
        ids (ObjectID): Get single mongoDB object id to filter out a single data from MongoDB database.
        payload (UUID): Get user_id from payload after authentication.

    Returns:
        return: Return single data (200) from mongodb by searching comment id and user_id else
        return no data found (404) or something wrong happened exception or bad
        request (400).
    """
    try:
        # check if cached response avaliable or not
        cached_item = cache.get(f"sentiment_analysis_by_{ids}_{payload['user_id']}")
        if cached_item:
            deserialized_data = json.loads(cached_item)
            response_data = json.dumps(deserialized_data, indent=4)
            return Response(response_data, status=200, mimetype='application/json')
        data = []
        comment = sentiment_analysis_db.find_one({"_id": ObjectId(ids), "user": uuid.UUID(payload['user_id'])})
        if comment is None:
            response_data = json.dumps({"msg": "data is not found."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        dict_item = OrderedDict([
            ("id", str(comment["_id"])),
            ("video_title", str(comment["video_title"])),
            ("video_url", str(comment["video_url"])),
            ("comment", str(comment["comment"])),
            ("main_result", str(comment["main_result"])),
            ("other_result", str(comment["other_result"])),
            ("user", str(comment["user"])),
        ])
        data.append(dict_item)
        response_data = json.dumps({"data": data}, indent=4)
        cache.set(f"sentiment_analysis_by_{ids}_{payload['user_id']}", response_data)
        return Response(response_data, status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')


@app.route("/delete-comment/<ids>", methods=['POST'])
@jwt_login_required
def delete_single_comment(ids, payload):
    """Delete single data from MongoDB database.

    Args:
        ids (ObjectID): Get single mongoDB object id to filter out a single data from MongoDB database.
        payload (UUID): Get user_id from payload after authentication.

    Returns:
        return: Finding the single data from mongodb by searching comment id and user_id then
        deleting that data (204) else return no data found (404) or something wrong happened exception or bad
        request (400).
    """
    try:
        comment = sentiment_analysis_db.find_one({"_id": ObjectId(ids), "user": uuid.UUID(payload['user_id'])})
        if comment is None:
            response_data = json.dumps({"msg": "data is not found."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        if comment:
            sentiment_analysis_db.delete_one({"_id": ObjectId(ids)})
            # deleting cache data
            cache.delete(f"sentiment_analysis_by_{ids}_{payload['user_id']}")
            rabbit_mq.publish("delete_data_from_youtools_django", ids)
        return Response({}, status=204, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')


@app.route("/all-categories", methods=['GET'])
@jwt_login_required
def get_all_categories(payload):
    """Get all the categories data from MongoDB database.

    Args:
        payload (UUID): Get user_id from payload after authentication. 

    Returns:
        return: Return all the categories data (200) from mongodb by searching user_id else
        return no data found (404) or something wrong happened exception or bad
        request (400).
    """
    try:
        # check if cached response avaliable or not
        cached_item = cache.get(f"categories_sentiment_analysis_all_data_{payload['user_id']}")
        if cached_item:
            deserialized_data = json.loads(cached_item)
            response_data = json.dumps(deserialized_data, indent=4)
            return Response(response_data, status=200, mimetype='application/json')
        
        data = []
        categories = category_db.find({"user": payload['user_id']})
        if category_db.count_documents({}) == 0:
            response_data = json.dumps({"msg": "categories is not found."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        for category in categories:
            dict_item = OrderedDict([
                ("id", str(category["_id"])),
                ("category_name", str(category["category_name"])),
                ("user", str(category["user"])),
            ])
            data.append(dict_item)
        response_data = json.dumps({"data": data}, indent=4)
        cache.set(f"categories_sentiment_analysis_all_data_{payload['user_id']}", response_data)
        return Response(response_data, status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')


@app.route("/delete-category/<category_id>", methods=['POST'])
@jwt_login_required
def delete_category(payload, category_id):
    """Delete specific category data from MongoDB.

    Args:
        payload (UUID): Get user_id from payload after authentication.
        category_id (ObjectID): Get single mongoDB category object id 
        to filter out a single category data from MongoDB database.

    Returns:
        return: Finding the single category data from mongodb by searching category id and user_id then
        checking if data found in category and if found then deleting specific category data (204) and
        deleting all that data releted to category (204) else return no data found (404) or something wrong happened exception or bad
        request (400).
    """
    try:
        category_data_find = category_db.find_one({"_id": ObjectId(category_id), "user": payload['user_id']})
        if not category_data_find:
            response_data = json.dumps({"msg": "category is not found."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        if category_data_find:
            category_db.delete_one({"_id": ObjectId(category_id)})
            sentiment_analysis_db.delete_many({"category": ObjectId(category_id)})
            cache.delete(f"sentiment_analysis_all_data_{payload['user_id']}_{category_id}")
            rabbit_mq.publish("delete_data_and_category_from_django_category", category_id)
        return Response({}, status=204, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')
