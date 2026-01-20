import requests
import os
from openai import OpenAI
from PyPDF2 import PdfReader
from dotenv import load_dotenv


DEVIN_API_KEY = os.getenv("DEVIN_API_KEY")
DEVIN_API_BASE_URL = "https://api.devin.ai/v1"

class Devin:     
    def __init__(self):
        load_dotenv()
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



class ChatGPT:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)

    def get_devin_prompt(self, prompt, response_format):
        input = [
            {
                "role": "system",
                "content": "You are a strict compiler of Devin execution prompts. Precision over verbosity."
            },
            {
                "role": "user",
                "content": prompt
            },
        ]

        if response_format is not None:
            input.append(
                {
                    "role": "user",
                    "content": (
                        "Your response MUST strictly follow the format below. "
                        "Do not add explanations, comments, or extra fields.\n\n"
                        f"{response_format}"
                    )
                    
                }
            )
            
        response = self.client.responses.create(
            model="gpt-5.2",
            reasoning={"effort": "high"},
            input=input
        )

        return response.output[1].content[0].text