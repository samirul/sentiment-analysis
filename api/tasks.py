"""
    Using celery task for fetching youtube comments from video
    using Youtube API and analysing comments using pretrained
    sentiment-analysis models from hugging face.
    After then saving results on MongoDB and converting to API
    using flask 

"""
import uuid
from celery import shared_task
from data_cleanup.clean_data import Filter
from sentiment_analysis.sentiment import SentiMental
from youtube_comments.get_youtube_comments import Comments
from api import sentiment_analysis_db, cache, category_db
from url_id_extractor.id_extract import get_id
from .producers import RabbitMQConnection


@shared_task(ignore_result=False, bind=True)
def task_run(self, video_url, payload, max_len, device='cuda', top_k=None):
    """Function for responsible executing celery task within class member

    Raises:
    ValueError: raises video url error if required youtube video url id is not provided before executing the task.
    ValueError: raises max len error if required length/total comments is not provided before executing the task.
    ValueError: raises payload error if user is not logged in before executing the task.

    Returns:
    returns: It execute and run task of sentiment analysis
    and save data on MongoDB and then returns Done, else will throw 
    an exception
    """

    try:
        total = max_len
        self.update_state(state='PENDING', meta={'current': 0, 'total': total})
        video_id = get_id(video_url)
        publish = RabbitMQConnection()
        progress = 0

        if not video_url:
            raise ValueError("Video url isn't found, please add a url.")
        if not max_len:
            raise ValueError("No max length is found.")
        if not payload:
            raise ValueError("User is not logged in, not user information has been found.")

        comments = Comments(video_id=video_id, max_len=max_len)
        titles = comments.fetch_title()
        comments = comments.fetch_comments()

        while comments:
            categories = category_db.find_one({"category_name": titles, "user": uuid.UUID(payload["user_id"])})
            if not categories:
                category_db.insert_one({"category_name": titles, "user": uuid.UUID(payload["user_id"])})

            if categories:
                data = comments.popleft() # getting unfiltered datas from queue
                cleaned_data = Filter(text=data) # filtering unfiltered data
                listed_cleaned_data = list(cleaned_data.clean()) # cleaned data
                sentiment_analysis = SentiMental(text=listed_cleaned_data, device=device, top_k=top_k)
                sentiment_analysis_main_data = sentiment_analysis.result_data_convertion().split(',', maxsplit=1)[0] #
                sentiment_analysis_aditional_data = ", ".join([item.strip() for item in sentiment_analysis.result_data_convertion().split(',')[1:]])
                data = sentiment_analysis_db.insert_one({"video_title": titles, "video_url": video_url,
                "comment": "".join(listed_cleaned_data), "main_result": sentiment_analysis_main_data,
                "other_result": sentiment_analysis_aditional_data, "user": uuid.UUID(payload['user_id']),
                "category": categories['_id']})
                cache.delete(f"sentiment_analysis_all_data_{payload['user_id']}_{categories['_id']}") # deleting caches
                data_inserted = sentiment_analysis_db.find_one({"_id": data.inserted_id, "user": uuid.UUID(payload['user_id'])})

                if isinstance(data_inserted["user"], uuid.UUID):
                    data_inserted["user"] = str(data_inserted["user"])

                if isinstance(categories["user"], uuid.UUID):
                    categories["user"] = str(categories["user"])

                publish.publish(method="task_category_saved", body=categories)
                publish.publish(method="task_data_saved", body=data_inserted)
                progress += 1
                self.update_state(state='RUNNING', meta={'current': progress, 'total': total})
        return {'current': total, 'total': total, 'status': 'Task completed!'}
    except Exception as e:
        print(f"Something is Wrong: {e}")
        return e