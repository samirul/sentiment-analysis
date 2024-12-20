"""     
    Added sentiment analysis model for analysis text if positive
    or negetive or nutral.
"""

from transformers import pipeline

class SentiMental:
    """Imported Required parameters"""
    def __init__(self, text, device='cuda', top_k=None):
        self.model = "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
        self.device = device
        self.top_k = top_k
        self.text = text

    def result_data(self):
        """Added required parameters to transformer pipelines
        Models, Device, Top_K

        Yields:
            generate: Feed data to pipeline and then get the results using generator.
        """
        try:
            if not self.text:
                raise ValueError("No text has been added.")
            
            sentiment_analysis_pipeline = pipeline(model=self.model,
            top_k=self.top_k, device=self.device                                                                                    
            )
            yield sentiment_analysis_pipeline(self.text)
        except Exception as e:
            yield str(e)

    def result_data_convertion(self):
        """Get result from pipeline

        Returns:
            return: Get result from sentiment anaysis
            pipeline and convert it to percentages
        """
        try:
            if not self.text:
                raise ValueError("No text has been added.")
            
            result = self.result_data()
            return " ".join([f"{round(data[0][0].get('score') * 100)}% {data[0][0].get('label').capitalize()}, {round(data[0][1].get('score') * 100)}% {data[0][1].get('label').capitalize()}, {round(data[0][2].get('score') * 100)}% {data[0][2].get('label').capitalize()}" for data in result])
        except Exception as e:
            return str(e)



