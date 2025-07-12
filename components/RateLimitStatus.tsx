'use client';

import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';

interface RateLimitInfo {
  remaining: number;
  wait_time: number;
}

interface RateLimits {
  openai: RateLimitInfo;
  serpapi: RateLimitInfo;
  perplexity: RateLimitInfo;
  linkedin_scrape: RateLimitInfo;
}

export default function RateLimitStatus() {
  const [rateLimits, setRateLimits] = useState<RateLimits | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRateLimits = async () => {
      try {
        const response = await fetch('/api/rate-limits');
        if (response.ok) {
          const data = await response.json();
          setRateLimits(data);
        }
      } catch (error) {
        console.error('Failed to fetch rate limits:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRateLimits();
    // Refresh every 30 seconds
    const interval = setInterval(fetchRateLimits, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return null;
  }

  if (!rateLimits) {
    return null;
  }

  const getStatusIcon = (remaining: number, waitTime: number) => {
    if (remaining > 0) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    } else if (waitTime > 0) {
      return <Clock className="h-4 w-4 text-yellow-500" />;
    } else {
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusText = (remaining: number, waitTime: number) => {
    if (remaining > 0) {
      return `${remaining} requests remaining`;
    } else if (waitTime > 0) {
      const minutes = Math.ceil(waitTime / 60);
      return `Wait ${minutes} min`;
    } else {
      return 'Rate limited';
    }
  };

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
      <h3 className="text-sm font-medium text-blue-900 mb-2">API Rate Limits</h3>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex items-center space-x-2">
          {getStatusIcon(rateLimits.openai.remaining, rateLimits.openai.wait_time)}
          <span className="text-blue-800">OpenAI:</span>
          <span className="text-blue-600">{getStatusText(rateLimits.openai.remaining, rateLimits.openai.wait_time)}</span>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon(rateLimits.serpapi.remaining, rateLimits.serpapi.wait_time)}
          <span className="text-blue-800">SerpAPI:</span>
          <span className="text-blue-600">{getStatusText(rateLimits.serpapi.remaining, rateLimits.serpapi.wait_time)}</span>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon(rateLimits.perplexity.remaining, rateLimits.perplexity.wait_time)}
          <span className="text-blue-800">Perplexity:</span>
          <span className="text-blue-600">{getStatusText(rateLimits.perplexity.remaining, rateLimits.perplexity.wait_time)}</span>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon(rateLimits.linkedin_scrape.remaining, rateLimits.linkedin_scrape.wait_time)}
          <span className="text-blue-800">LinkedIn:</span>
          <span className="text-blue-600">{getStatusText(rateLimits.linkedin_scrape.remaining, rateLimits.linkedin_scrape.wait_time)}</span>
        </div>
      </div>
    </div>
  );
} 