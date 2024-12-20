from sentiment_analysis.sentiment import SentiMental

def test_sentiment_analysis():
    text = "He is good person."
    sentiment = SentiMental(text=text)
    assert 'label' in list(sentiment.result_data())[0][0][0]
    assert 'score' in list(sentiment.result_data())[0][0][0]
    assert sentiment.result_data_convertion() == '97% Positive, 2% Neutral, 0% Negative'


def test_sentiment_analysis_failed_for_not_text():
    text = ""
    sentiment = SentiMental(text=text)
    assert 'label' not in list(sentiment.result_data())[0]
    assert 'score' not in list(sentiment.result_data())[0]
    assert list(sentiment.result_data())[0] == "No text has been added."
    assert sentiment.result_data_convertion() == "No text has been added."