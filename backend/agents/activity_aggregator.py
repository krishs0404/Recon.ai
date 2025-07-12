import httpx
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from .rate_limiter import rate_limiter

load_dotenv()

class ActivityAggregator:
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def aggregate_activities(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Aggregate recent public activities for the person
        """
        name = profile_data.get('name', '')
        headline = profile_data.get('headline', '')
        
        activities = []
        
        try:
            # Search for recent activities using Perplexity API
            if self.perplexity_key:
                activities.extend(await self._search_perplexity(name, headline))
            
            # Fallback to SerpAPI
            if self.serpapi_key:
                activities.extend(await self._search_serpapi(name, headline))
            
            # If no API keys, return mock data
            if not activities:
                activities = self._get_mock_activities(name)
                
        except Exception as e:
            # Return mock data on error
            activities = self._get_mock_activities(name)
        
        return activities
    
    async def _search_perplexity(self, name: str, headline: str) -> List[Dict[str, Any]]:
        """
        Search for recent activities using Perplexity API
        """
        # Check rate limit
        if not rate_limiter.is_allowed('perplexity'):
            print("Rate limit exceeded for Perplexity API, skipping...")
            return []
        
        try:
            query = f"Recent news, blog posts, conference talks, or public activities by {name} {headline} in the last 6 months"
            
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 1000
            }
            
            response = await self.session.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            content = result['choices'][0]['message']['content']
            
            # Parse the response into structured activities
            activities = []
            lines = content.split('\n')
            current_activity = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    if current_activity:
                        activities.append(current_activity)
                    current_activity = {
                        'title': line[1:].strip(),
                        'type': 'activity',
                        'source': 'perplexity'
                    }
                elif line and current_activity:
                    current_activity['description'] = line
            
            if current_activity:
                activities.append(current_activity)
            
            return activities
            
        except Exception as e:
            print(f"Perplexity API error: {e}")
            return []
    
    async def _search_serpapi(self, name: str, headline: str) -> List[Dict[str, Any]]:
        """
        Search for recent activities using SerpAPI
        """
        # Check rate limit
        if not rate_limiter.is_allowed('serpapi'):
            print("Rate limit exceeded for SerpAPI, skipping...")
            return []
        
        try:
            search_query = f"{name} {headline} news blog conference 2024"
            url = "https://serpapi.com/search"
            params = {
                'q': search_query,
                'api_key': self.serpapi_key,
                'engine': 'google',
                'num': 10
            }
            
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            activities = []
            for result in data.get('organic_results', [])[:5]:
                activities.append({
                    'title': result.get('title', ''),
                    'description': result.get('snippet', ''),
                    'url': result.get('link', ''),
                    'type': 'search_result',
                    'source': 'serpapi'
                })
            
            return activities
            
        except Exception as e:
            print(f"SerpAPI error: {e}")
            return []
    
    def _get_mock_activities(self, name: str) -> List[Dict[str, Any]]:
        """
        Return mock activities for demo purposes
        """
        return [
            {
                'title': f'{name} gave a keynote at the WHO Global Health Summit',
                'description': 'Discussed the future of pandemic preparedness and vaccine equity.',
                'type': 'conference',
                'source': 'mock'
            },
            {
                'title': 'Featured in The Economist: “How AI is Changing Global Health”',
                'description': 'Bill Gates shared his vision for AI-driven diagnostics.',
                'type': 'news',
                'source': 'mock'
            },
            {
                'title': 'Published “The Road to Net Zero” on Gates Notes',
                'description': 'Explores climate tech investments and policy.',
                'type': 'blog',
                'source': 'mock'
            },
            {
                'title': f'{name} invested in climate-focused startups',
                'description': 'Announced new funding for carbon capture technology.',
                'type': 'news',
                'source': 'mock'
            }
        ] 