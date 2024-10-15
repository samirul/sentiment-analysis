from celery import shared_task
from data_cleanup.clean_data import Filter
from sentiment_analysis.sentiment import SentiMental
from youtube_comments.get_youtube_comments import Comments
from api import sentiment_analysis_db


class Procressing:
    def __init__(self, video_id, max_len=20, device='cuda', top_k=None):
        self.comments = Comments(video_id=video_id, max_len=max_len)
        self.device = device
        self.top_k = top_k

    def task(self):
        comments = self.comments.fetch_comments()
        while comments:
             data = comments.popleft()
             cleaned_data = Filter(text=data)
             listed_cleaned_data = list(cleaned_data.clean()) #
             sentiment_analysis = SentiMental(text=listed_cleaned_data, device=self.device, top_k=self.top_k)
             sentiment_analysis_main_data = sentiment_analysis.result_data_convertion().split(',', maxsplit=1)[0] #
             sentiment_analysis_aditional_data = ", ".join([item.strip() for item in sentiment_analysis.result_data_convertion().split(',')[1:]])
             sentiment_analysis_db.insert_one({"comment": "".join(listed_cleaned_data), "main_result": sentiment_analysis_main_data, "other_result": sentiment_analysis_aditional_data})
        return "Done"



@shared_task(ignore_result=False)
def task_celery_execute(video_id, max_len=20):
    process = Procressing(video_id=video_id, max_len=max_len)
    process.task()