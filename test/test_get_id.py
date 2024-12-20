from url_id_extractor.id_extract import get_id

def test_get_id_from_youtube_link():
    url = "https://www.youtube.com/watch?v=r0m-iSnbKvc"
    assert get_id(url) == 'r0m-iSnbKvc'


def test_get_id_from_youtube_link_failed_for_no_url():
    url = None
    assert get_id(url) == "No url is found."
