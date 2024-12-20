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


class Procressing:
    """Intializing some required parameters"""
    def __init__(self, video_url, payload, max_len, device='cuda', top_k=None):
        self.video_id = get_id(video_url)
        self.video_url = video_url
        self.max_len = max_len
        self.comments = None
        self.device = device
        self.top_k = top_k
        self.publish = RabbitMQConnection()
        self.payload = payload

    def task(self):
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
            if not self.video_url:
                raise ValueError("Video url isn't found, please add a url.")
            if not self.max_len:
                raise ValueError("No max length is found.")
            if not self.payload:
                raise ValueError("User is not logged in, not user information has been found.")
            
            self.comments = Comments(video_id=self.video_id, max_len=self.max_len)
            comments = self.comments.fetch_comments()
            titles = self.comments.fetch_title()

            while comments:
                categories = category_db.find_one({"category_name": titles, "user": uuid.UUID(self.payload["user_id"])})
                if not categories:
                    category_db.insert_one({"category_name": titles, "user": uuid.UUID(self.payload["user_id"])})

                if categories:
                    data = comments.popleft() # getting unfiltered datas from queue
                    cleaned_data = Filter(text=data) # filtering unfiltered data
                    listed_cleaned_data = list(cleaned_data.clean()) # cleaned data
                    sentiment_analysis = SentiMental(text=listed_cleaned_data, device=self.device, top_k=self.top_k)
                    sentiment_analysis_main_data = sentiment_analysis.result_data_convertion().split(',', maxsplit=1)[0] #
                    sentiment_analysis_aditional_data = ", ".join([item.strip() for item in sentiment_analysis.result_data_convertion().split(',')[1:]])
                    data = sentiment_analysis_db.insert_one({"video_title": titles, "video_url": self.video_url,
                    "comment": "".join(listed_cleaned_data), "main_result": sentiment_analysis_main_data,
                    "other_result": sentiment_analysis_aditional_data, "user": uuid.UUID(self.payload['user_id']),
                    "category": categories['_id']})
                    cache.delete(f"sentiment_analysis_all_data_{self.payload['user_id']}_{categories['_id']}") # deleting caches
                    data_inserted = sentiment_analysis_db.find_one({"_id": data.inserted_id, "user": uuid.UUID(self.payload['user_id'])})

                    if isinstance(data_inserted["user"], uuid.UUID):
                        data_inserted["user"] = str(data_inserted["user"])

                    if isinstance(categories["user"], uuid.UUID):
                        categories["user"] = str(categories["user"])

                    self.publish.publish(method="task_category_saved", body=categories)
                    self.publish.publish(method="task_data_saved", body=data_inserted)
            return "Done"
        except Exception as e:
            print(f"Something is Wrong: {e}")
            return e


@shared_task(ignore_result=False)
def task_celery_execute(video_url, payload, max_len):
    """Function for warping up celery "shared_task" for excecuting
        celery task

    Args:
        video_url (Link): Youtube video url id.
        payload (auth, sting, uuid): Getting user id from the access token after login from django.
        application youtools.
        max_len (int): max times fetching youtube comments. Defaults to 20.

    Returns:
        Returns: Return done if task run successfully, else will thow error if task failed to execute.
    """

    try:
        process = Procressing(video_url=video_url, payload=payload, max_len=max_len)
        process.task()
        return "Done"
    except Exception as e:
        print(f"Something is Wrong ->: {e}")
        return e