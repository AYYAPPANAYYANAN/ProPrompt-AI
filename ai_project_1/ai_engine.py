
import os
import groq

class TextAnalyzer:
    def __init__(self):
        self.groq_api_key = os.environ['GROQ_API_KEY']
        self.groq_client = groq.Client(self.groq_api_key)

    def analyze_text(self, text):
        summary_response = self.groq_client.query('text/summarize', {'text': text})
        sentiment_response = self.groq_client.query('text/sentiment', {'text': text})
        return summary_response['summary'], sentiment_response['sentiment']
