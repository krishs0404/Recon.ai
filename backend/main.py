from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from agents.scraper_agent import ScraperAgent
from agents.activity_aggregator import ActivityAggregator
from agents.llm_agent import LLMAgent
from agents.rate_limiter import rate_limiter
from agents.public_updates_agent import PublicUpdatesAgent

app = FastAPI(title="Recon API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    linkedinUrl: str

class AnalyzeResponse(BaseModel):
    summary: str
    questions: list[str]

class PublicUpdatesRequest(BaseModel):
    updates_block: str

class PublicUpdatesResponse(BaseModel):
    key_updates: list[str]
    questions: list[str]

@app.get("/")
async def root():
    return {"message": "Recon API"}

@app.get("/api/rate-limits")
async def get_rate_limits():
    """Get current rate limit status for all APIs"""
    return {
        "openai": {
            "remaining": rate_limiter.get_remaining_requests('openai'),
            "wait_time": rate_limiter.get_wait_time('openai')
        },
        "serpapi": {
            "remaining": rate_limiter.get_remaining_requests('serpapi'),
            "wait_time": rate_limiter.get_wait_time('serpapi')
        },
        "perplexity": {
            "remaining": rate_limiter.get_remaining_requests('perplexity'),
            "wait_time": rate_limiter.get_wait_time('perplexity')
        },
        "linkedin_scrape": {
            "remaining": rate_limiter.get_remaining_requests('linkedin_scrape'),
            "wait_time": rate_limiter.get_wait_time('linkedin_scrape')
        }
    }

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_profile(request: AnalyzeRequest):
    try:
        # Initialize agents
        scraper = ScraperAgent()
        aggregator = ActivityAggregator()
        llm_agent = LLMAgent()
        
        # Step 1: Scrape LinkedIn profile
        profile_data = await scraper.scrape_profile(request.linkedinUrl)
        
        # Step 2: Aggregate recent activities
        activities = await aggregator.aggregate_activities(profile_data)
        
        # Step 3: Generate summary and questions
        structured = await llm_agent.generate_summary_and_questions(profile_data, activities)
        
        return AnalyzeResponse(
            summary=structured.get('summary', ''),
            questions=structured.get('questions', [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/public-updates", response_model=PublicUpdatesResponse)
async def public_updates(request: PublicUpdatesRequest):
    try:
        agent = PublicUpdatesAgent()
        result = await agent.analyze_updates(request.updates_block)
        return PublicUpdatesResponse(
            key_updates=result.get('key_updates', []),
            questions=result.get('questions', [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 