"""
    get video id from youtube video url
"""

from urllib.parse import urlparse, parse_qs

def get_id(url):
    """function for extract id from the url

    Args:
        url (Link): Getting the url link as parameter

    Returns:
        return: returning the url id after extracting from
        url the link using urllib else returning None 
    """
    normal_url = ['www.youtube.com', 'youtube.com']
    url_parsed = urlparse(url=url)
    # getting id from sorted video url
    if url_parsed.hostname == 'youtu.be':
        return url_parsed.path[1:]
    # getting id from normal video url
    if url_parsed.hostname in normal_url:
        get_query_params = parse_qs(url_parsed.query)
        return get_query_params.get('v', [None])[0]
    return None