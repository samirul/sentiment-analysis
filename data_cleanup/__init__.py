"""
    downloading all the nltk stopwords files before running clean_data python scripts.
"""

import nltk


nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
