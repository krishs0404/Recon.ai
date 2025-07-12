import os
from typing import Dict, Any
from dotenv import load_dotenv
from .rate_limiter import rate_limiter
import openai
import json

load_dotenv()

class PublicUpdatesAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def analyze_updates(self, updates_block: str) -> Dict[str, Any]:
        """
        Analyze a block of recent public updates and generate:
        - 2–4 key updates (summarized)
        - 3–5 smart, specific questions tied to those updates
        """
        try:
            prompt = self._build_prompt(updates_block)
            response = await self._call_openai(prompt)
            structured = self._parse_structured_response(response)
            return structured
        except Exception as e:
            return self._get_mock_structured_response()

    def _build_prompt(self, updates_block: str) -> str:
        prompt = f'''
You are a networking research assistant. Given a block of recent public updates (tweets, blog headlines, talk quotes, etc.), do the following:

1. Summarize 2–4 key updates as clear, short bullet points.
2. Write 3–5 smart, specific networking questions, each directly tied to the content of the updates. Avoid generic or vague questions.

Input:
"""
{updates_block.strip()}
"""

Output JSON with keys: key_updates (list of strings), questions (list of strings).
'''
        return prompt

    async def _call_openai(self, prompt: str) -> str:
        if not rate_limiter.is_allowed('openai'):
            raise Exception("Rate limit exceeded for OpenAI API. Please try again later.")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful networking assistant. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=600,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content if content else ""
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise e

    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            data = json.loads(json_str)
            return {
                "key_updates": data.get("key_updates", []),
                "questions": data.get("questions", [])
            }
        except Exception as e:
            print(f"Error parsing structured response: {e}")
            return {
                "key_updates": [],
                "questions": []
            }

    def _get_mock_structured_response(self) -> Dict[str, Any]:
        return {
            "key_updates": [
                "Funding AI-powered malaria diagnostics in Africa",
                "Concerned about global pandemic preparedness gaps",
                "Promoting AI’s role in future disaster prediction"
            ],
            "questions": [
                "You recently highlighted AI in climate forecasting—what technical gaps do you see in making that a reality?",
                "What made you prioritize malaria diagnostics now?",
                "What do you think is the most overlooked lesson from COVID?"
            ]
        } 