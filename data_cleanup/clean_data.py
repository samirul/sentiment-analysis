"""
    Clean all bad/garbage texts to clean texts for analysis.
"""

import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class Filter:
    """Filter class for filtering garbage text to clean text.

    Yields:
        generator: "generates filtered/cleaned data one by one or at a time."
    """
    def __init__(self, text):
        self.text = text
        # initializing lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        # setting english stopwords
        self.stop_words = set(stopwords.words('english'))

    def clean(self):
        """Responsible for cleaning all the text.

        Raises:
            ValueError: raises if no text is found for cleaning data.
            TypeError: raises if provided text is not string type.

        Yields:
            generator: "function generates filtered/cleaned data one by one or at a time."
        """
        try:
            if not self.text:
                raise ValueError("No text is found for cleaning data.")
            if not isinstance(self.text, str):
                raise TypeError(f"Text should be in string and not {type(self.text)}.")
            
            text = self.text.lower() # converting every text into smaller case
            removing_urls = re.sub(r"http\S+|www\S+|https\S+", '', text, flags=re.MULTILINE) # removing urls from the text
            removing_href = re.sub(r"href+",'', removing_urls) # removing href from the text
            remove_special_characters_from_text = re.sub(r"\W+", ' ', removing_href) # removing special characters from the text
            remove_digits_from_text = re.sub(r"\d+", '', remove_special_characters_from_text) # removing digits from the text
            removing_emojis = re.sub(r"[^\x00-\x7F]+", '', remove_digits_from_text) # removing emojis from the text
            
            cleaned_text = removing_emojis
            tokenize_text = word_tokenize(cleaned_text) # tokenizing text or breaking into words
            # removing stop words
            removing_stop_words_from_tokenize_text = [words for words in tokenize_text if words not in self.stop_words]
            # Lemmatizing_words
            lemmatize_words = [self.lemmatizer.lemmatize(removed_stop_words_) for removed_stop_words_ in removing_stop_words_from_tokenize_text]
            cleaned_final_text = " ".join(lemmatize_words) # joining all the cleaned words back to final text

            yield cleaned_final_text

        except Exception as e:
            yield e



