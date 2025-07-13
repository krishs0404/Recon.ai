import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.public_content_fetcher import fetch_public_content
from agents.entity_graph_builder import build_entity_graph
from agents.graph_retriever import retrieve_relevant_context
from agents.question_generator import generate_questions

async def test_elite_pipeline():
    """Test the complete elite pipeline"""
    
    print("🚀 Testing Elite Recon Pipeline")
    print("=" * 50)
    
    # Test person
    test_person = "Bill Gates"
    
    try:
        # Step 1: Fetch public content
        print(f"\n📡 Step 1: Fetching content for {test_person}")
        content = await fetch_public_content(test_person)
        
        if not content:
            print("❌ No content found")
            return
        
        print(f"✅ Found {len(content)} content updates")
        
        # Step 2: Build entity graph
        print(f"\n🕸️ Step 2: Building entity graph")
        graph = await build_entity_graph(content)
        
        print(f"✅ Built graph with {graph['graph_stats']['node_count']} nodes, {graph['graph_stats']['edge_count']} edges")
        
        # Show some graph nodes
        print("\n📊 Sample graph nodes:")
        for node in graph['nodes'][:5]:
            print(f"  - {node['id']} ({node['type']})")
        
        # Step 3: Retrieve relevant context
        print(f"\n🔍 Step 3: Retrieving relevant context")
        context = await retrieve_relevant_context(
            content=content,
            graph=graph,
            query="climate change and philanthropy",
            max_chunks=5
        )
        
        print(f"✅ Retrieved {len(context['relevant_chunks'])} relevant chunks")
        
        # Show relevant chunks
        print("\n📝 Sample relevant chunks:")
        for i, chunk in enumerate(context['relevant_chunks'][:3]):
            print(f"  {i+1}. {chunk['title'][:50]}...")
            print(f"     Score: {chunk['relevance_score']:.2f}")
        
        # Step 4: Generate questions
        print(f"\n❓ Step 4: Generating questions")
        
        # Convert chunks to update format
        relevant_updates = []
        for chunk in context['relevant_chunks'][:5]:
            relevant_updates.append({
                "source": chunk.get("source", "Unknown"),
                "title": chunk.get("title", ""),
                "snippet": chunk.get("text", ""),
                "date": chunk.get("date", "")
            })
        
        questions_result = await generate_questions(relevant_updates, 3)
        
        print(f"✅ Generated {len(questions_result)} questions")
        
        # Show questions
        print("\n🤔 Generated questions:")
        for i, question in enumerate(questions_result[:3]):
            print(f"  {i+1}. {question.get('question', '')[:80]}...")
        
        # Step 5: Summary
        print(f"\n📊 Pipeline Summary:")
        print(f"  - Content updates: {len(content)}")
        print(f"  - Graph nodes: {graph['graph_stats']['node_count']}")
        print(f"  - Graph edges: {graph['graph_stats']['edge_count']}")
        print(f"  - Relevant chunks: {len(context['relevant_chunks'])}")
        print(f"  - Questions generated: {len(questions_result)}")
        
        print("\n🎉 Elite pipeline test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in elite pipeline test: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_individual_components():
    """Test individual components"""
    
    print("\n🧪 Testing Individual Components")
    print("=" * 40)
    
    # Test entity graph builder
    print("\n🕸️ Testing Entity Graph Builder")
    test_content = [
        {
            "source": "TechCrunch",
            "title": "Bill Gates invests in climate tech startup",
            "snippet": "Microsoft co-founder Bill Gates has invested $50M in CarbonCapture Inc, a startup focused on direct air capture technology.",
            "date": "2024-01-15"
        },
        {
            "source": "Gates Notes",
            "title": "Bill Gates speaks at COP28 about climate innovation",
            "snippet": "At the recent COP28 summit, Bill Gates emphasized the importance of breakthrough energy technologies in combating climate change.",
            "date": "2024-01-10"
        }
    ]
    
    try:
        graph = await build_entity_graph(test_content)
        print(f"✅ Graph built: {graph['graph_stats']['node_count']} nodes, {graph['graph_stats']['edge_count']} edges")
        
        # Test graph retriever
        print("\n🔍 Testing Graph Retriever")
        context = await retrieve_relevant_context(
            content=test_content,
            graph=graph,
            query="climate investment",
            max_chunks=3
        )
        print(f"✅ Context retrieved: {len(context['relevant_chunks'])} chunks")
        
    except Exception as e:
        print(f"❌ Component test error: {str(e)}")

if __name__ == "__main__":
    # Run tests
    asyncio.run(test_individual_components())
    asyncio.run(test_elite_pipeline()) 