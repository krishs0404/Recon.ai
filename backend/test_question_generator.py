import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.question_generator import generate_questions

async def test_generate_questions():
    """Test the generate_questions function with example data"""
    
    # Test data from the requirements
    updates = [
        {
            "source": "GatesNotes",
            "title": "Why We're Investing $20M in Malaria Diagnostics",
            "snippet": "We're funding scalable diagnostic platforms across Sub-Saharan Africa...",
            "date": "2024-11-10"
        },
        {
            "source": "Breakthrough Energy Summit",
            "title": "The Role of AI in Disaster Prediction",
            "snippet": "Bill Gates emphasized AI's role in climate modeling for flood forecasting...",
            "date": "2025-02-15"
        }
    ]
    
    print("🧪 Testing generate_questions() function...")
    print(f"Input updates: {len(updates)} items")
    
    try:
        # Test with default temperature
        questions = await generate_questions(updates)
        
        print(f"\n✅ Success! Generated {len(questions)} questions:")
        for i, q in enumerate(questions, 1):
            print(f"\n{i}. Question: {q['question']}")
            print(f"   Based on: {q['based_on']}")
        
        # Validate structure
        assert isinstance(questions, list), "Questions should be a list"
        assert 3 <= len(questions) <= 5, f"Expected 3-5 questions, got {len(questions)}"
        
        for q in questions:
            assert 'question' in q, "Each question should have 'question' key"
            assert 'based_on' in q, "Each question should have 'based_on' key"
            assert isinstance(q['question'], str), "Question should be a string"
            assert isinstance(q['based_on'], str), "Based_on should be a string"
        
        print("\n✅ All structure validations passed!")
        
        # Test with custom temperature
        print("\n🧪 Testing with custom temperature (0.3)...")
        questions_custom = await generate_questions(updates, temperature=0.3)
        print(f"Generated {len(questions_custom)} questions with custom temperature")
        
        # Test with empty updates
        print("\n🧪 Testing with empty updates...")
        empty_questions = await generate_questions([])
        assert empty_questions == [], "Empty updates should return empty list"
        print("✅ Empty updates handled correctly")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_generate_questions())
    if success:
        print("\n🚀 Question generator is ready for production!")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        sys.exit(1) 