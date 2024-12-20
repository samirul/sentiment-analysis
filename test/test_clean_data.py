from youtube_comments.get_youtube_comments import Comments
from data_cleanup.clean_data import Filter

def test_clean_datas():
    comm = Comments(video_id='r0m-iSnbKvc', max_len=5)
    da = comm.fetch_comments()
    total = []
    while da:
        da_ = da.popleft()
        filter_ = Filter(text=da_)
        data = list(filter_.clean())
        total.append(data)
    assert len(total) == 5
    assert total[0][0] == 'limited time get software development program'


