from openai import OpenAI
from dotenv import load_dotenv
import os

from helpers.logger import Logger

load_dotenv()
OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")

class ChatGPT:
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPEN_AI_API_KEY)
        self._logger = Logger("openAI-operator")
    
    def generate_response(self, description: str) -> str:
        response = self.openai_client.responses.create(
            model="gpt-4o",
            instructions="This is an issue from Home Assistant. Suggest the best and most straightforward solution. Format the response as a well-structured HTML email, including <html>, <head>, and <body>. Return no triple backticks. Do not include any closing remarks, sign-offs, or sender details.",
            input=description,
        )
        return response.output_text


