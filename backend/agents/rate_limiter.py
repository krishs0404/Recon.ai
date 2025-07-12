import time
from typing import Dict, Optional
from collections import defaultdict
import asyncio

class RateLimiter:
    def __init__(self):
        self.request_counts = defaultdict(list)
        self.limits = {
            'openai': {'requests': 10, 'window': 3600},  # 10 requests per hour
            'serpapi': {'requests': 20, 'window': 3600},  # 20 requests per hour
            'perplexity': {'requests': 15, 'window': 3600},  # 15 requests per hour
            'linkedin_scrape': {'requests': 5, 'window': 3600},  # 5 requests per hour
        }
    
    def is_allowed(self, api_type: str) -> bool:
        """
        Check if a request is allowed based on rate limits
        """
        if api_type not in self.limits:
            return True
        
        current_time = time.time()
        window = self.limits[api_type]['window']
        max_requests = self.limits[api_type]['requests']
        
        # Clean old requests outside the window
        self.request_counts[api_type] = [
            req_time for req_time in self.request_counts[api_type]
            if current_time - req_time < window
        ]
        
        # Check if we're under the limit
        if len(self.request_counts[api_type]) < max_requests:
            self.request_counts[api_type].append(current_time)
            return True
        
        return False
    
    def get_remaining_requests(self, api_type: str) -> int:
        """
        Get remaining requests for an API type
        """
        if api_type not in self.limits:
            return 999999  # Large number instead of float('inf')
        
        current_time = time.time()
        window = self.limits[api_type]['window']
        max_requests = self.limits[api_type]['requests']
        
        # Clean old requests
        self.request_counts[api_type] = [
            req_time for req_time in self.request_counts[api_type]
            if current_time - req_time < window
        ]
        
        return max(0, max_requests - len(self.request_counts[api_type]))
    
    def get_wait_time(self, api_type: str) -> float:
        """
        Get time to wait before next request is allowed
        """
        if api_type not in self.limits:
            return 0
        
        current_time = time.time()
        window = self.limits[api_type]['window']
        
        if not self.request_counts[api_type]:
            return 0
        
        oldest_request = min(self.request_counts[api_type])
        return max(0, window - (current_time - oldest_request))

# Global rate limiter instance
rate_limiter = RateLimiter() 