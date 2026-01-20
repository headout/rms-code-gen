import requests
import os
from openai import OpenAI
from prompts.inventory_prompt_result_format import META_PROMPT_REZDY, META_PROMPT_REZDY_RESULT
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

DEVIN_API_KEY = os.getenv("DEVIN_API_KEY")
DEVIN_API_BASE_URL = "https://api.devin.ai/v1"

class Devin:     
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {DEVIN_API_KEY}",
            "Content-Type": "application/json",
        }

    def create_new_devin_session(self, prompt):
        try:
            response = requests.post(
                url = DEVIN_API_BASE_URL+"/sessions",
                json={"prompt": prompt},
                headers=self.headers,
            )
        except Exception as e:
            raise Exception("error in making request to devin: ", e)

        return response.json()["session_id"]


    def get_session_status(self, session_id):
        try:
            response = requests.get(
                DEVIN_API_BASE_URL + f"/sessions/{session_id}",
                headers=self.headers,
            )
        except Exception as e:
            raise Exception("error in making request to devin: ", e)

        return response.json()["status_enum"]
    

    def send_followp_message_on_session(self, session_id, prompt):
        try:
            response = requests.post(
                url=DEVIN_API_BASE_URL + f"/sessions/{session_id}/message",
                json={"message": prompt},
                headers=self.headers,
            )
        except Exception as e:
            raise Exception("error in making request to devin: ", e)
        
        return True
