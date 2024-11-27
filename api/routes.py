""" 
    Here route act as endpoint for link
    and for writing certain logics.

"""
import uuid
import json
from collections import OrderedDict
from bson.objectid import ObjectId
from flask import request, jsonify, Response
from api import app, sentiment_analysis_db, cache
from api.tasks import task_celery_execute
from jwt_token.jwt_token_verify import jwt_login_required

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
        result = task_celery_execute.delay(video_url=inputed_text, payload=payload)
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
        return: Return all the data (200) from mongodb by searching user_id else
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
        sentiment_analysis_db.delete_one({"_id": ObjectId(ids)})
        # deleting cache data
        cache.delete(f"sentiment_analysis_by_{ids}_{payload['user_id']}")
        return Response({}, status=204, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')