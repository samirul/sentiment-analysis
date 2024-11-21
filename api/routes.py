""" 
    Here route act as endpoint for link
    and for writing certain logics.

"""
import uuid
import json
from collections import OrderedDict
from flask import request, jsonify, Response
from api import app, sentiment_analysis_db
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
    
@app.route("/all-youtube-comments-results", methods=['GET'])
@jwt_login_required
def get_all_comments_and_results(payload):
    """Get all the data from MongoDB database

    Args:
        payload (string): get user_id from 

    Returns:
        _type_: _description_
    """
    try:
        data = []
        comments = sentiment_analysis_db.find({"user": uuid.UUID(payload['user_id'])})
        if sentiment_analysis_db.count_documents({}) == 0:
            response_data = json.dumps({"msg": "data is not found."}, indent=4)
            return Response(response_data, status=404, mimetype='application/json')
        for comment in comments:
            dict_items = OrderedDict([
                ("id", str(comment["_id"])),
                ("video_title", str(comment["video_title"])),
                ("video_url", str(comment["video_url"])),
                ("comment", str(comment["comment"])),
                ("main_result", str(comment["main_result"])),
                ("other_result", str(comment["other_result"])),
                ("user", str(comment["user"])),
            ])  
            data.append(dict_items)
        response_data = json.dumps({"data": data}, indent=4)
        return Response(response_data, status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        response_data = json.dumps({"msg": "Something is wrong or bad request"}, indent=4)
        return Response(response_data, status=400, mimetype='application/json')
