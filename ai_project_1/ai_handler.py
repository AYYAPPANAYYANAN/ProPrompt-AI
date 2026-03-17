
import os
import groq

class AIHandler:
   def __init__(self):
       self.groq_api_key = os.environ.get('GROQ_API_KEY')
       self.groq_client = groq.Client(self.groq_api_key)

   def respond(self, message):
       prompt = """You are a Senior Engineering Manager. Respond to the user's input: 
       '{}'""".format(message)
       response = self.groq_client.generate(prompt)
       return response
