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
        self.max_len = max_len # maximum comments are allowed to fetch

    def fetch_comments(self):
        """fetching youtube comments.

        Raises:
            ValueError: raise if video id is not found.
            ValueError: raise if max length is not found.
            ValueError: raise if max length value is less than 1.
            TypeError: raise if max length is not integer type.
            TypeError: raise if video id is not string type.

        Returns:
            return: "Queue for storing comments temporary(FIFO)."
        """
        try:
            if not self.video_id:
                raise ValueError("Video id is not found.")
            if not self.max_len:
                raise ValueError("Max length is not found.")
            if isinstance(self.max_len, int) and self.max_len < 1:
                raise ValueError(f"Max length should be atleast 1 and not {self.max_len}.")
            if not isinstance(self.max_len, int):
                raise TypeError(f"Max length should be integer and not {type(self.max_len)}.")
            if not isinstance(self.video_id, str):
                raise TypeError(f"Video id should be string and not {type(self.video_id)}.")
            
            request = self.youtube.commentThreads().list(part="snippet", videoId=self.video_id, maxResults=self.max_len) # pylint: disable=E1101
            response = request.execute()
            # getting you tube comments and storing them in the queue
            for item in response['items']:
                comments = item['snippet']['topLevelComment']['snippet']['textDisplay']
                queue.appendleft(comments)
            return queue
        except Exception as e:
            return e
    
    def fetch_title(self):
        """fetching youtube title.

        Raises:
            ValueError: raise if video id is not found.
            TypeError: raise if video id is not string type.

        Returns:
            return: get video title from youtube api.
        """
        try:
            if not self.video_id:
                raise ValueError("Video id is not found.")
            if not isinstance(self.video_id, str):
                raise TypeError(f"Video id should be string and not {type(self.video_id)}.")
            request = self.youtube.videos().list(part='snippet,statistics', id=self.video_id) # pylint: disable=E1101
            response = request.execute()
            # getting youtube video title name
            title = response['items'][0]['snippet']['title']
            return title
        except Exception as e:
            return e
    
    