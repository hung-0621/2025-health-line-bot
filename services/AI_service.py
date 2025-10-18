import json
import google.genai as genai
from config import config
from google.genai import types


class AIService:
    def __init__(self):
        self.GEMENI_API_KEY = config.GOOGLE_GEMENI_API_KEY

    # 讀取指令檔案
    def _get_instruction(self) -> str:
        with open("assets/json/AI_instruction.json", "r", encoding="utf-8") as f:
            instruction_data = json.load(f)
            instruction = instruction_data["message"]
        return instruction

    # 產生回應
    def generate_response(self, prompt: str) -> str:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=self._get_instruction()
            ),
            contents=prompt,
        )

        return response.text
