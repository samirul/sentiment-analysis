"""
    Getting required youtube comments from youtube channel video.
"""

import os
from googleapiclient.discovery import build
from youtube_comments import queue

class Comments:
    """ class for fetching comments from youtube video using youtube api.

    Returns:
        return: Queue and Title.
    """
    def __init__(self, video_id, max_len):
        self.api_key = os.environ.get('YOUTUBE_API_KEY') # Getting api key from env variable
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.video_id = video_id # getting youtube id
        self.max_len = max_len + 1 # maximum comments is allowed to fetch

    def fetch_comments(self):
        """fetching youtube comments.

        Returns:
            return: "Queue for storing comments temporary(FIFO)."
        """
        request = self.youtube.commentThreads().list(part="snippet", videoId=self.video_id, maxResults=self.max_len) # pylint: disable=E1101
        response = request.execute()
        # getting you tube comments and storing them in the queue
        for item in response['items']:
            comments = item['snippet']['topLevelComment']['snippet']['textDisplay']
            queue.append(comments)
        
        return queue
    
    def fetch_title(self):
        """fetching youtube title.

        Returns:
            return: get video title from youtube api.
        """
        request = self.youtube.videos().list(part='snippet,statistics', id=self.video_id) # pylint: disable=E1101
        response = request.execute()
        # getting youtube video title name
        title = response['items'][0]['snippet']['title']
        return title
    
    