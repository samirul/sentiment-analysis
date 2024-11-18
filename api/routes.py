from flask import request, jsonify
from api import app
from api.tasks import task_celery_execute

@app.route("/analysis-youtube-comments", methods=["POST"])
def analysis_comments_from_youtube():
    try:
        inputed_text = request.json.get("url")
        result = task_celery_execute.delay(video_url=inputed_text)
        return jsonify({"msg": "Success", "result_id": result.id}),200
    except Exception as e:
        print(e)
        return jsonify({"msg": "Something is wrong or bad request"}),400