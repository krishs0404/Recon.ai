import openai
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from .rate_limiter import rate_limiter
import json

load_dotenv()

class QuestionGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_questions(
        self, 
        updates: List[Dict[str, Any]], 
        temperature: float = 0.7
    ) -> List[Dict[str, str]]:
        """
        Generate 3-5 smart, non-generic, reference-grounded questions based on recent public updates.
        
        Args:
            updates: List of dictionaries with keys: source, title, snippet, date
            temperature: Temperature for GPT-4 Turbo (default: 0.7)
            
        Returns:
            List of dictionaries with keys: question, based_on
        """
        try:
            if not updates:
                return []
                
            prompt = self._build_prompt(updates)
            response = await self._call_openai(prompt, temperature)
            questions = self._parse_questions_response(response)
            return questions
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_fallback_questions(updates)

    def _build_prompt(self, updates: List[Dict[str, Any]]) -> str:
        """Build the prompt for GPT-4 Turbo"""
        
        # Format updates into readable context
        updates_text = ""
        for i, update in enumerate(updates, 1):
            source = update.get('source', 'Unknown')
            title = update.get('title', '')
            snippet = update.get('snippet', '')
            date = update.get('date', '')
            
            updates_text += f"{i}. Source: {source}\n"
            updates_text += f"   Title: {title}\n"
            updates_text += f"   Snippet: {snippet}\n"
            if date:
                updates_text += f"   Date: {date}\n"
            updates_text += "\n"
        
        prompt = f"""
You are an expert networking assistant. Given the following recent public updates about a person, generate 3-5 smart, non-generic questions that someone could ask them in a networking conversation.

Each question should:
- Be grounded in specific content from the updates
- Show genuine interest and knowledge
- Be conversational and engaging
- Reference specific details from the updates
- Avoid generic questions like "How are you?" or "What do you do?"

Recent Updates:
{updates_text}

Generate 3-5 questions and return them as a JSON array. Each question should be an object with:
- "question": The actual question text
- "based_on": The specific title/source this question is based on

Example format:
[
    {{
        "question": "What motivated your focus on malaria diagnostics now, and how do you think AI will accelerate the rollout?",
        "based_on": "Why We're Investing $20M in Malaria Diagnostics"
    }},
    {{
        "question": "At the Breakthrough Energy Summit, you emphasized AI in flood forecasting—what technical bottlenecks do you think remain?",
        "based_on": "The Role of AI in Disaster Prediction"
    }}
]

Return only valid JSON.
"""
        return prompt

    async def _call_openai(self, prompt: str, temperature: float) -> str:
        """Call OpenAI GPT-4 Turbo API"""
        if not rate_limiter.is_allowed('openai'):
            raise Exception("Rate limit exceeded for OpenAI API. Please try again later.")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful networking assistant. Generate insightful, specific questions based on recent updates. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                            max_tokens=1000,
            temperature=min(temperature, 2.0)  # Cap temperature at 2.0
            )
            content = response.choices[0].message.content
            return content if content else ""
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise e

    def _parse_questions_response(self, response: str) -> List[Dict[str, str]]:
        """Parse the OpenAI response into structured questions"""
        try:
            # Find JSON in response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start == -1 or end == 0:
                return []
            
            json_str = response[start:end]
            questions = json.loads(json_str)
            
            # Validate structure
            validated_questions = []
            for q in questions:
                if isinstance(q, dict) and 'question' in q and 'based_on' in q:
                    validated_questions.append({
                        'question': str(q['question']),
                        'based_on': str(q['based_on'])
                    })
            
            return validated_questions
            
        except Exception as e:
            print(f"Error parsing questions response: {e}")
            return []

    def _get_fallback_questions(self, updates: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate fallback questions when API fails"""
        fallback_questions = []
        
        for update in updates[:3]:  # Limit to first 3 updates
            title = update.get('title', '')
            source = update.get('source', '')
            
            if title:
                question = f"What inspired your recent work on '{title}'?"
                fallback_questions.append({
                    'question': question,
                    'based_on': title
                })
        
        # Add a generic question if we have no specific ones
        if not fallback_questions and updates:
            fallback_questions.append({
                'question': "What's been the most exciting development in your recent work?",
                'based_on': 'Recent updates'
            })
        
        return fallback_questions

# Standalone function for direct use
async def generate_questions(updates: List[Dict[str, Any]], temperature: float = 0.7) -> List[Dict[str, str]]:
    """
    Standalone function to generate questions from public updates.
    
    Args:
        updates: List of dictionaries with keys: source, title, snippet, date
        temperature: Temperature for GPT-4 Turbo (default: 0.7)
        
    Returns:
        List of dictionaries with keys: question, based_on
    """
    generator = QuestionGenerator()
    return await generator.generate_questions(updates, temperature) 