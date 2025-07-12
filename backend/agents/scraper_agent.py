import re
import httpx
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from .rate_limiter import rate_limiter

load_dotenv()

class ScraperAgent:
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.session = httpx.AsyncClient(timeout=30.0)
    
    async def scrape_profile(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Scrape LinkedIn profile data from URL or search by name
        """
        try:
            # Check if input is a LinkedIn URL
            if "linkedin.com" in linkedin_url:
                return await self._scrape_linkedin_url(linkedin_url)
            else:
                # Treat as name and search
                return await self._search_by_name(linkedin_url)
        except Exception as e:
            # Fallback to mock data for demo
            return self._get_mock_profile_data(linkedin_url)
    
    async def _scrape_linkedin_url(self, url: str) -> Dict[str, Any]:
        """
        Attempt to scrape LinkedIn profile (Note: LinkedIn blocks most scraping)
        """
        # Check rate limit
        if not rate_limiter.is_allowed('linkedin_scrape'):
            raise Exception("Rate limit exceeded for LinkedIn scraping. Please try again later.")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = await self.session.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic info (this is simplified - real scraping would be more complex)
            name = soup.find('h1')
            headline = soup.find('div', {'class': 'text-body-medium'})
            about = soup.find('section', {'class': 'summary'})
            
            return {
                'name': name.text.strip() if name else 'Unknown',
                'headline': headline.text.strip() if headline else '',
                'about': about.text.strip() if about else '',
                'url': url,
                'source': 'linkedin_scrape'
            }
        except Exception as e:
            raise Exception(f"Failed to scrape LinkedIn URL: {str(e)}")
    
    async def _search_by_name(self, name: str) -> Dict[str, Any]:
        """
        Search for person by name using SerpAPI
        """
        if not self.serpapi_key:
            raise Exception("SERPAPI_KEY not configured")
        
        # Check rate limit
        if not rate_limiter.is_allowed('serpapi'):
            raise Exception("Rate limit exceeded for SerpAPI. Please try again later.")
        
        try:
            search_query = f"{name} site:linkedin.com"
            url = "https://serpapi.com/search"
            params = {
                'q': search_query,
                'api_key': self.serpapi_key,
                'engine': 'google'
            }
            
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract LinkedIn profile from search results
            for result in data.get('organic_results', []):
                if 'linkedin.com/in/' in result.get('link', ''):
                    return await self._scrape_linkedin_url(result['link'])
            
            # If no LinkedIn profile found, return basic info
            return {
                'name': name,
                'headline': 'Professional',
                'about': f'Information about {name}',
                'url': '',
                'source': 'search'
            }
            
        except Exception as e:
            raise Exception(f"Failed to search by name: {str(e)}")
    
    def _get_mock_profile_data(self, input_data: str) -> Dict[str, Any]:
        """
        Return mock profile data for demo purposes
        """
        if "linkedin.com" in input_data:
            name = "Bill Gates"
        else:
            name = input_data
        
        return {
            'name': name,
            'headline': 'Co-Chair, Bill & Melinda Gates Foundation | Co-founder, Microsoft',
            'about': 'Bill Gates is a technologist, business leader, and philanthropist. He is passionate about global health, education, and climate innovation.',
            'url': input_data if "linkedin.com" in input_data else '',
            'posts': [
                "Shared insights on malaria vaccine progress (June 2024)",
                "Commented on AI's role in global health (May 2024)",
                "Posted about the Breakthrough Energy Summit (April 2024)"
            ],
            'skills': ['Philanthropy', 'Technology', 'Climate Change', 'Global Health'],
            'projects': [
                "Breakthrough Energy Ventures",
                "Gates Notes Blog"
            ],
            'source': 'mock'
        } 