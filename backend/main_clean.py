from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from agents.scraper_agent import ScraperAgent
from agents.public_content_fetcher import fetch_public_content
from agents.question_generator import generate_questions
from agents.llm_agent import LLMAgent
from agents.rate_limiter import rate_limiter

app = FastAPI(title="Recon API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    linkedinUrl: str

class AnalyzeResponse(BaseModel):
    summary: str
    questions: list[str]

class FetchContentRequest(BaseModel):
    name_or_url: str

class FetchContentResponse(BaseModel):
    updates: list[dict]

class GenerateQuestionsRequest(BaseModel):
    updates: list[dict]
    temperature: float = 0.7

class GenerateQuestionsResponse(BaseModel):
    questions: list[dict]

# ============================================================================
# CORE PIPELINE ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {"message": "Recon API - Smart Networking Intelligence"}

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
        }
    }

# ============================================================================
# PIPELINE 1: COMPLETE ANALYSIS (LinkedIn URL → Summary + Questions)
# ============================================================================

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_profile(request: AnalyzeRequest):
    """
    Complete pipeline: LinkedIn URL → Profile + Activities → Summary + Questions
    
    This is the main endpoint for comprehensive analysis.
    """
    try:
        # Step 1: Extract LinkedIn profile data
        scraper = ScraperAgent()
        profile_data = await scraper.scrape_profile(request.linkedinUrl)
        
        # Step 2: Fetch recent public content
        updates = await fetch_public_content(profile_data.get('name', 'Unknown'))
        
        # Step 3: Generate summary using LLM
        llm_agent = LLMAgent()
        summary = await llm_agent.generate_summary(profile_data, updates)
        
        # Step 4: Generate smart questions
        questions_data = await generate_questions(updates)
        questions = [q.get('question', '') for q in questions_data]
        
        return AnalyzeResponse(
            summary=summary,
            questions=questions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PIPELINE 2: CONTENT DISCOVERY (Name/URL → Recent Updates)
# ============================================================================

@app.post("/api/fetch-content", response_model=FetchContentResponse)
async def fetch_content_endpoint(request: FetchContentRequest):
    """
    Fetch recent public content for any person.
    
    This is useful for:
    - Researching someone before meeting them
    - Getting recent updates about anyone
    - Preparing for networking conversations
    """
    try:
        updates = await fetch_public_content(request.name_or_url)
        return FetchContentResponse(updates=updates)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PIPELINE 3: QUESTION GENERATION (Updates → Smart Questions)
# ============================================================================

@app.post("/api/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_questions_endpoint(request: GenerateQuestionsRequest):
    """
    Generate smart networking questions from public updates.
    
    This is useful for:
    - Creating conversation starters
    - Preparing for interviews
    - Building relationships
    """
    try:
        questions = await generate_questions(request.updates, request.temperature)
        return GenerateQuestionsResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PIPELINE 4: QUICK ANALYSIS (Name → Questions Only)
# ============================================================================

@app.post("/api/quick-questions", response_model=GenerateQuestionsResponse)
async def quick_questions_endpoint(request: FetchContentRequest):
    """
    Quick pipeline: Name → Content → Questions
    
    This is the fastest way to get smart questions about someone.
    """
    try:
        # Step 1: Fetch content
        updates = await fetch_public_content(request.name_or_url)
        
        # Step 2: Generate questions
        questions = await generate_questions(updates)
        
        return GenerateQuestionsResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 