from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Dict, Any, Optional
import asyncio

# Import our elite modules
from agents.scraper_agent import ScraperAgent
from agents.public_content_fetcher import fetch_public_content
from agents.entity_graph_builder import build_entity_graph
from agents.graph_retriever import retrieve_relevant_context
from agents.question_generator import generate_questions
from agents.llm_agent import LLMAgent
from agents.rate_limiter import rate_limiter

app = FastAPI(title="Recon Elite API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class BriefingRequest(BaseModel):
    name_or_url: str
    query: Optional[str] = None
    max_questions: int = 5
    include_graph: bool = True

class BriefingResponse(BaseModel):
    summary: str
    questions: List[Dict[str, Any]]
    updates: List[Dict[str, Any]]
    graph: Optional[Dict[str, Any]] = None
    context_summary: str
    sources: List[str]
    cached: bool = False
    retrieval_method: str

class PublicContentRequest(BaseModel):
    name_or_url: str

class GenerateQuestionsRequest(BaseModel):
    updates: List[Dict[str, Any]]
    temperature: float = 0.7

# ============================================================================
# ELITE BRIEFING PIPELINE
# ============================================================================

@app.post("/api/briefing", response_model=BriefingResponse)
async def generate_elite_briefing(request: BriefingRequest):
    """
    🚀 ELITE BRIEFING PIPELINE
    
    Complete GraphRAG-powered networking briefing:
    1. Fetch public content
    2. Build entity graph
    3. Retrieve relevant context
    4. Generate smart questions
    5. Return structured briefing
    """
    try:
        # Rate limiting check
        if not rate_limiter.is_allowed("openai"):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        print(f"🎯 Starting elite briefing for: {request.name_or_url}")
        
        # Step 1: Fetch public content
        print("📡 Step 1: Fetching public content...")
        content = await fetch_public_content(request.name_or_url)
        
        if not content:
            raise HTTPException(
                status_code=404, 
                detail=f"No public content found for {request.name_or_url}"
            )
        
        print(f"✅ Found {len(content)} content updates")
        
        # Step 2: Build entity graph
        print("🕸️ Step 2: Building entity graph...")
        graph = await build_entity_graph(content)
        
        print(f"✅ Built graph with {graph['graph_stats']['node_count']} nodes, {graph['graph_stats']['edge_count']} edges")
        
        # Step 3: Retrieve relevant context using GraphRAG
        print("🔍 Step 3: Retrieving relevant context...")
        context = await retrieve_relevant_context(
            content=content,
            graph=graph,
            query=request.query,
            max_chunks=5
        )
        
        print(f"✅ Retrieved {len(context['relevant_chunks'])} relevant chunks")
        
        # Step 4: Generate questions from relevant context
        print("❓ Step 4: Generating smart questions...")
        
        # Convert relevant chunks back to update format for question generation
        relevant_updates = []
        for chunk in context['relevant_chunks'][:5]:  # Top 5 chunks
            relevant_updates.append({
                "source": chunk.get("source", "Unknown"),
                "title": chunk.get("title", ""),
                "snippet": chunk.get("text", ""),
                "date": chunk.get("date", "")
            })
        
        questions_result = await generate_questions(relevant_updates, request.max_questions)
        
        # Step 5: Generate summary using LLM
        print("📝 Step 5: Generating summary...")
        llm_agent = LLMAgent()
        
        # Create context summary for LLM
        context_text = "\n".join([
            f"{chunk['title']}: {chunk['text']}" 
            for chunk in context['relevant_chunks'][:3]
        ])
        
        summary = await llm_agent.generate_summary(
            profile_data={"name": request.name_or_url},
            updates=relevant_updates
        )
        
        # Extract sources
        sources = []
        for update in content:
            if isinstance(update, dict) and "source" in update:
                sources.append(update["source"])
        sources = list(set(sources))
        
        # Create context summary
        from agents.graph_retriever import GraphRetriever
        retriever = GraphRetriever()
        relevant_chunks = context.get('relevant_chunks', []) if isinstance(context, dict) else []
        context_summary = retriever.get_context_summary(relevant_chunks)
        
        print("🎉 Elite briefing completed successfully!")
        
        return BriefingResponse(
            summary=summary,
            questions=questions_result,  # questions_result is already a list
            updates=content,
            graph=graph if request.include_graph else None,
            context_summary=context_summary,
            sources=sources,
            cached=False,  # TODO: Implement caching
            retrieval_method=context.get("retrieval_method", "graphrag_hybrid") if isinstance(context, dict) else "graphrag_hybrid"
        )
        
    except Exception as e:
        print(f"❌ Error in elite briefing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Briefing generation failed: {str(e)}")

# ============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# ============================================================================

@app.post("/api/fetch-public-content")
async def fetch_public_content_endpoint(request: PublicContentRequest):
    """Fetch public content for a person."""
    try:
        if not rate_limiter.is_allowed("serpapi"):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        content = await fetch_public_content(request.name_or_url)
        return {"content": content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-questions")
async def generate_questions_endpoint(request: GenerateQuestionsRequest):
    """Generate questions from updates."""
    try:
        if not rate_limiter.is_allowed("openai"):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        questions = await generate_questions(request.updates, temperature=request.temperature)
        return questions
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/api/rate-limits")
async def get_rate_limits():
    """Get current rate limit status."""
    return {
        "openai_remaining": rate_limiter.get_remaining_requests("openai"),
        "serpapi_remaining": rate_limiter.get_remaining_requests("serpapi"),
        "perplexity_remaining": rate_limiter.get_remaining_requests("perplexity")
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "pipeline": "elite_graphrag"
    }

# ============================================================================
# DEVELOPMENT ENDPOINTS
# ============================================================================

@app.post("/api/debug/graph")
async def debug_build_graph(request: PublicContentRequest):
    """Debug endpoint to build entity graph."""
    try:
        content = await fetch_public_content(request.name_or_url)
        graph = await build_entity_graph(content)
        return {
            "content_count": len(content),
            "graph": graph
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/debug/retrieve")
async def debug_retrieve_context(request: BriefingRequest):
    """Debug endpoint to test context retrieval."""
    try:
        content = await fetch_public_content(request.name_or_url)
        graph = await build_entity_graph(content)
        context = await retrieve_relevant_context(
            content=content,
            graph=graph,
            query=request.query
        )
        return {
            "content_count": len(content),
            "graph_stats": graph["graph_stats"],
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 