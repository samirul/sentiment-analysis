"""
    Using celery task for fetching youtube comments from video
    using Youtube API and analysing comments using pretrained
    sentiment-analysis models from hugging face.
    After then saving results on MongoDB and converting to API
    using flask 

"""

from celery import shared_task
from data_cleanup.clean_data import Filter
from sentiment_analysis.sentiment import SentiMental
from youtube_comments.get_youtube_comments import Comments
from api import sentiment_analysis_db
from url_id_extractor.id_extract import get_id
from .producers import RabbitMQConnection


class Procressing:
    """Intializing some required parameters"""
    def __init__(self, video_url, payload, max_len=20, device='cuda', top_k=None):
        self.video_id = get_id(video_url)
        self.video_url = video_url
        self.comments = Comments(video_id=self.video_id, max_len=max_len)
        self.device = device
        self.top_k = top_k
        self.publish = RabbitMQConnection()
        self.payload = payload

    def task(self):
        """Function for responsible executing celery task within class member

        Returns:
            returns: It execute and run task of sentiment analysis
            and save on MongoDB and then returns Done, else will throw 
            an exception
        """
        try:
            comments = self.comments.fetch_comments()
            titles = self.comments.fetch_title()
            while comments:
                data = comments.popleft() # getting unfiltered datas from queue
                cleaned_data = Filter(text=data) # filtering unfiltered data
                listed_cleaned_data = list(cleaned_data.clean()) # cleaned data
                sentiment_analysis = SentiMental(text=listed_cleaned_data, device=self.device, top_k=self.top_k)
                sentiment_analysis_main_data = sentiment_analysis.result_data_convertion().split(',', maxsplit=1)[0] #
                sentiment_analysis_aditional_data = ", ".join([item.strip() for item in sentiment_analysis.result_data_convertion().split(',')[1:]])
                data = sentiment_analysis_db.insert_one({"video_title": titles, "video_url": self.video_url,
                "comment": "".join(listed_cleaned_data), "main_result": sentiment_analysis_main_data,
                "other_result": sentiment_analysis_aditional_data, "user": self.payload['user_id']})
                data_inserted = sentiment_analysis_db.find_one({"_id": data.inserted_id})
                self.publish.publish(method="task_data_saved", body=data_inserted)
            return "Done"
        except Exception as e:
            return e


@shared_task(ignore_result=False)
def task_celery_execute(video_url, payload, max_len=20):
    """Function for warping up celery "shared_task" for excecuting
        celery task

    Args:
        video_url (Link): Youtube video url
        max_len (int, optional): max fetching youtube comments. Defaults to 20.
    """
    process = Procressing(video_url=video_url, payload=payload, max_len=max_len)
    process.task()