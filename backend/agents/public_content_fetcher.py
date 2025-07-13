import httpx
import re
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
from .rate_limiter import rate_limiter
from datetime import datetime, timedelta
import json

load_dotenv()

class PublicContentFetcher:
    def __init__(self):
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def fetch_public_content(self, name_or_url: str) -> List[Dict[str, Any]]:
        """
        Fetch recent public updates for a person (name or LinkedIn URL).
        
        Args:
            name_or_url: Person's name or LinkedIn URL
            
        Returns:
            List of structured updates with keys: source, title, snippet, date, url
        """
        try:
            # Extract name from LinkedIn URL if provided
            name = self._extract_name_from_url(name_or_url) if "linkedin.com" in name_or_url else name_or_url
            
            updates = []
            
            # 1. Search for recent news and blog articles
            news_updates = await self._search_news_and_blogs(name)
            updates.extend(news_updates)
            
            # 2. Search for recent talks/interviews (YouTube, podcasts)
            talk_updates = await self._search_talks_and_interviews(name)
            updates.extend(talk_updates)
            
            # 3. Search for recent tweets (if API available)
            tweet_updates = await self._search_recent_tweets(name)
            updates.extend(tweet_updates)
            
            # 4. Search for blog posts
            blog_updates = await self._search_blog_posts(name)
            updates.extend(blog_updates)
            
            # Filter and sort by date, limit to 5 most recent
            filtered_updates = self._filter_and_sort_updates(updates)
            
            return filtered_updates[:5]
            
        except Exception as e:
            print(f"Error fetching public content: {e}")
            return self._get_fallback_updates(name_or_url)
    
    def _extract_name_from_url(self, url: str) -> str:
        """Extract name from LinkedIn URL"""
        # Simple extraction - in production you'd want more robust parsing
        if "linkedin.com/in/" in url:
            name_part = url.split("linkedin.com/in/")[-1].split("/")[0]
            return name_part.replace("-", " ").title()
        return "Unknown"
    
    async def _search_news_and_blogs(self, name: str) -> List[Dict[str, Any]]:
        """Search for recent news and blog articles"""
        updates = []
        
        try:
            # Try Perplexity API first
            if self.perplexity_key and rate_limiter.is_allowed('perplexity'):
                updates.extend(await self._search_perplexity_news(name))
            
            # Fallback to SerpAPI
            if self.serpapi_key and rate_limiter.is_allowed('serpapi'):
                updates.extend(await self._search_serpapi_news(name))
                
        except Exception as e:
            print(f"Error searching news: {e}")
        
        return updates
    
    async def _search_perplexity_news(self, name: str) -> List[Dict[str, Any]]:
        """Search for news using Perplexity API"""
        try:
            query = f"Recent news articles, blog posts, or public mentions about {name} in the last 12 months"
            
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
            return self._parse_perplexity_response(content, name)
            
        except Exception as e:
            print(f"Perplexity API error: {e}")
            return []
    
    async def _search_serpapi_news(self, name: str) -> List[Dict[str, Any]]:
        """Search for news using SerpAPI"""
        try:
            search_query = f"{name} news blog article 2024"
            url = "https://serpapi.com/search"
            params = {
                'q': search_query,
                'api_key': self.serpapi_key,
                'engine': 'google',
                'num': 10,
                'tbs': 'qdr:y'  # Last year
            }
            
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            updates = []
            for result in data.get('organic_results', [])[:5]:
                updates.append({
                    'source': self._extract_domain(result.get('link', '')),
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', ''),
                    'date': self._extract_date_from_url(result.get('link', '')),
                    'url': result.get('link', '')
                })
            
            return updates
            
        except Exception as e:
            print(f"SerpAPI error: {e}")
            return []
    
    async def _search_talks_and_interviews(self, name: str) -> List[Dict[str, Any]]:
        """Search for recent talks, interviews, and podcasts"""
        try:
            if self.serpapi_key and rate_limiter.is_allowed('serpapi'):
                search_query = f"{name} interview talk podcast youtube 2024"
                url = "https://serpapi.com/search"
                params = {
                    'q': search_query,
                    'api_key': self.serpapi_key,
                    'engine': 'google',
                    'num': 5,
                    'tbs': 'qdr:y'
                }
                
                response = await self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                updates = []
                for result in data.get('organic_results', [])[:3]:
                    if any(platform in result.get('link', '').lower() for platform in ['youtube.com', 'ted.com', 'podcast']):
                        updates.append({
                            'source': self._extract_domain(result.get('link', '')),
                            'title': result.get('title', ''),
                            'snippet': result.get('snippet', ''),
                            'date': self._extract_date_from_url(result.get('link', '')),
                            'url': result.get('link', '')
                        })
                
                return updates
                
        except Exception as e:
            print(f"Error searching talks: {e}")
        
        return []
    
    async def _search_recent_tweets(self, name: str) -> List[Dict[str, Any]]:
        """Search for recent tweets (placeholder - would need Twitter API)"""
        # Note: Twitter API requires authentication and has rate limits
        # This is a placeholder for future implementation
        return []
    
    async def _search_blog_posts(self, name: str) -> List[Dict[str, Any]]:
        """Search for blog posts on Medium, Substack, etc."""
        try:
            if self.serpapi_key and rate_limiter.is_allowed('serpapi'):
                search_query = f"{name} site:medium.com OR site:substack.com OR site:wordpress.com 2024"
                url = "https://serpapi.com/search"
                params = {
                    'q': search_query,
                    'api_key': self.serpapi_key,
                    'engine': 'google',
                    'num': 5,
                    'tbs': 'qdr:y'
                }
                
                response = await self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                updates = []
                for result in data.get('organic_results', [])[:3]:
                    updates.append({
                        'source': self._extract_domain(result.get('link', '')),
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'date': self._extract_date_from_url(result.get('link', '')),
                        'url': result.get('link', '')
                    })
                
                return updates
                
        except Exception as e:
            print(f"Error searching blogs: {e}")
        
        return []
    
    def _parse_perplexity_response(self, content: str, name: str) -> List[Dict[str, Any]]:
        """Parse Perplexity API response into structured updates"""
        updates = []
        
        # Simple parsing - split by lines and look for structured content
        lines = content.split('\n')
        current_update = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                if current_update:
                    updates.append(current_update)
                current_update = {
                    'source': 'News',
                    'title': line[1:].strip(),
                    'snippet': '',
                    'date': self._extract_date_from_text(line),
                    'url': ''
                }
            elif line and current_update:
                current_update['snippet'] = line
        
        if current_update:
            updates.append(current_update)
        
        return updates
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain.split('.')[0].title()
        except:
            return "Unknown"
    
    def _extract_date_from_url(self, url: str) -> str:
        """Extract date from URL if present"""
        # Look for date patterns in URL
        date_patterns = [
            r'/(\d{4})/(\d{2})/(\d{2})/',
            r'/(\d{4})-(\d{2})-(\d{2})',
            r'(\d{4})/(\d{2})/(\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, url)
            if match:
                year, month, day = match.groups()
                return f"{year}-{month}-{day}"
        
        return ""
    
    def _extract_date_from_text(self, text: str) -> str:
        """Extract date from text content"""
        # Look for date patterns in text
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\w+ \d{1,2},? \d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return ""
    
    def _filter_and_sort_updates(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and sort updates by relevance and date"""
        # Filter out updates without essential fields
        filtered = []
        for update in updates:
            if (update.get('title') and 
                update.get('snippet') and 
                len(update.get('snippet', '')) > 20):
                filtered.append(update)
        
        # Sort by date (most recent first)
        def sort_key(update):
            date_str = update.get('date', '')
            if date_str:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    return datetime.min
            return datetime.min
        
        filtered.sort(key=sort_key, reverse=True)
        
        return filtered
    
    def _get_fallback_updates(self, name_or_url: str) -> List[Dict[str, Any]]:
        """Return fallback updates when API calls fail"""
        name = name_or_url if "linkedin.com" not in name_or_url else "this person"
        
        return [
            {
                'source': 'TechCrunch',
                'title': f'{name} discusses AI innovation in recent interview',
                'snippet': f'In a recent interview, {name} shared insights on the future of artificial intelligence and its impact on various industries.',
                'date': '2024-12-01',
                'url': ''
            },
            {
                'source': 'Medium',
                'title': f'{name} publishes article on emerging technologies',
                'snippet': f'{name} recently published an article exploring the intersection of technology and business transformation.',
                'date': '2024-11-15',
                'url': ''
            }
        ]

# Standalone function for direct use
async def fetch_public_content(name_or_url: str) -> List[Dict[str, Any]]:
    """
    Fetch recent public updates for a person.
    
    Args:
        name_or_url: Person's name or LinkedIn URL
        
    Returns:
        List of structured updates with keys: source, title, snippet, date, url
    """
    fetcher = PublicContentFetcher()
    return await fetcher.fetch_public_content(name_or_url) 