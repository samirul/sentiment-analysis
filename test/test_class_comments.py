from youtube_comments import queue
from youtube_comments.get_youtube_comments import Comments

def test_class_comments_and_titile():
    while queue:
        queue.popleft()
    comments = Comments(video_id='r0m-iSnbKvc', max_len=1)
    fetch_comment = comments.fetch_comments()
    fetch_video_title = comments.fetch_title()
    assert len(fetch_comment) == 1
    assert fetch_video_title == 'How To Make Money From Python - A Complete Guide'


def test_class_comments_and_titile_failed_if_no_video_id_provided():
    while queue:
        queue.popleft()
    comments = Comments(video_id='', max_len=1)
    fetch_comment = comments.fetch_comments()
    fetch_video_title = comments.fetch_title()
    assert str(fetch_comment) == "Video id is not found."
    assert str(fetch_video_title) == "Video id is not found."

def test_class_comments_failed_if_no_max_len_provided():
    while queue:
        queue.popleft()
    max_len = None
    comments = Comments(video_id='r0m-iSnbKvc', max_len=max_len)
    fetch_comment = comments.fetch_comments()
    fetch_video_title = comments.fetch_title()
    assert str(fetch_comment) == "Max length is not found."
    assert str(fetch_video_title) == 'How To Make Money From Python - A Complete Guide'

def test_class_comments_failed_if_max_len_provided_less_than_one():
    while queue:
        queue.popleft()
    max_len = -1
    comments = Comments(video_id='r0m-iSnbKvc', max_len=max_len)
    fetch_comment = comments.fetch_comments()
    fetch_video_title = comments.fetch_title()
    assert str(fetch_comment) == f"Max length should be atleast 1 and not {max_len}."
    assert str(fetch_video_title) == 'How To Make Money From Python - A Complete Guide'


def test_class_comments_failed_if_max_len_provided_not_integer():
    while queue:
        queue.popleft()
    max_len = '1'
    comments = Comments(video_id='r0m-iSnbKvc', max_len=max_len)
    fetch_comment = comments.fetch_comments()
    fetch_video_title = comments.fetch_title()
    print(fetch_comment)
    assert str(fetch_comment) == f"Max length should be integer and not {type(max_len)}."
    assert str(fetch_video_title) == 'How To Make Money From Python - A Complete Guide'


def test_class_comments_and_titile_failed_if_video_id_is_not_string_provided():
    while queue:
        queue.popleft()
    video_id = 485795
    comments = Comments(video_id=video_id, max_len=1)
    fetch_comment = comments.fetch_comments()
    fetch_video_title = comments.fetch_title()
    assert str(fetch_comment) == f"Video id should be string and not {type(video_id)}."
    assert str(fetch_video_title) == f"Video id should be string and not {type(video_id)}."

