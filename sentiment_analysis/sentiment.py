from transformers import pipeline

class SentiMental:
    def __init__(self, text, device='cuda', top_k=None):
        self.model = "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
        self.device = device
        self.top_k = top_k
        self.text = text

    
    def result_data(self):
        sentiment_analysis_pipeline = pipeline(model=self.model,
        top_k=self.top_k, device=self.device                                                                                                           
        )

        yield sentiment_analysis_pipeline(self.text)

    def result_data_convertion(self):
        result = self.result_data()
        return " ".join([f"{round(data[0][0].get('score') * 100)}% {data[0][0].get('label').capitalize()}, {round(data[0][1].get('score') * 100)}% {data[0][1].get('label').capitalize()}, {round(data[0][2].get('score') * 100)}% {data[0][2].get('label').capitalize()}" for data in result])



