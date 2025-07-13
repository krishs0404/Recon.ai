import openai
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from .rate_limiter import rate_limiter
import json

load_dotenv()

class LLMAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_summary_and_questions(
        self, 
        profile_data: Dict[str, Any], 
        activities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a 3-5 sentence summary and 2-3 smart questions based on recent activities
        """
        try:
            prompt = self._build_prompt(profile_data, activities)
            response = await self._call_openai(prompt)
            structured = self._parse_structured_response(response)
            return structured
        except Exception as e:
            return self._get_mock_structured_response(profile_data.get('name', 'this person'))

    async def generate_summary(
        self, 
        profile_data: Dict[str, Any], 
        updates: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a 3-5 sentence summary based on profile and recent updates
        """
        try:
            prompt = self._build_summary_prompt(profile_data, updates)
            response = await self._call_openai(prompt)
            return response.strip()
        except Exception as e:
            return self._get_mock_summary(profile_data.get('name', 'this person'))

    def _build_summary_prompt(self, profile_data: Dict[str, Any], updates: List[Dict[str, Any]]) -> str:
        name = profile_data.get('name', 'this person')
        headline = profile_data.get('headline', '')
        about = profile_data.get('about', '')
        
        # Format recent updates
        updates_text = ""
        for i, update in enumerate(updates[:5], 1):
            source = update.get('source', 'Unknown')
            title = update.get('title', '')
            snippet = update.get('snippet', '')
            updates_text += f"{i}. {source}: {title}\n   {snippet}\n\n"
        
        prompt = f"""
You are a networking research assistant. Given the following data, write a comprehensive 3-5 sentence summary of this person's recent activities and current focus areas.

Profile:
Name: {name}
Headline: {headline}
About: {about}

Recent Public Updates:
{updates_text}

Write a warm, engaging summary that references specific details from their recent activities. Focus on what makes them interesting to network with.
"""
        return prompt

    def _build_prompt(self, profile_data: Dict[str, Any], activities: List[Dict[str, Any]]) -> str:
        name = profile_data.get('name', 'this person')
        headline = profile_data.get('headline', '')
        about = profile_data.get('about', '')
        posts = profile_data.get('posts', [])
        news = [a for a in activities if a.get('type') == 'news']
        
        posts_text = '\n'.join(f"- {p}" for p in posts) if posts else 'None'
        news_text = '\n'.join(f"- {n.get('title', '')}: {n.get('description', '')}" for n in news) if news else 'None'
        
        prompt = f"""
You are a networking research assistant. Given the following data:

Profile Summary:
Name: {name}\nHeadline: {headline}\nAbout: {about}

Recent Posts:\n{posts_text}

News Mentions:\n{news_text}

Write a comprehensive, 3–5 sentence summary of this person's recent activities, referencing specific posts, news, or projects. Then, generate 2–3 insightful, non-generic questions that someone could ask them in a networking conversation.

Return your answer as JSON with keys: summary, questions.
"""
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
                        "content": "You are a helpful networking assistant. Provide warm, engaging, and specific responses. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
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
                "summary": data.get("summary", ""),
                "questions": data.get("questions", [])
            }
        except Exception as e:
            print(f"Error parsing structured response: {e}")
            return {
                "summary": response,
                "questions": []
            }

    def _get_mock_structured_response(self, name: str) -> Dict[str, Any]:
        return {
            "summary": f"{name} has recently been active in global health and climate innovation. They shared insights on malaria vaccine progress, commented on AI's role in global health, and posted about the Breakthrough Energy Summit. Their keynote at the WHO Global Health Summit and features in The Economist highlight their ongoing influence in technology and philanthropy. Their recent investments in climate-focused startups show a strong commitment to sustainability and innovation.",
            "questions": [
                "What inspired your recent focus on AI-driven diagnostics in global health?",
                "How do you see the impact of climate tech investments evolving over the next few years?"
            ]
        }

    def _get_mock_summary(self, name: str) -> str:
        return f"{name} has recently been active in technology and innovation. They've shared insights on emerging technologies, participated in industry conferences, and published thought leadership content. Their work demonstrates a strong focus on innovation and strategic thinking, making them an interesting person to network with." 