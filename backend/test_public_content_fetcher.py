import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.public_content_fetcher import fetch_public_content

async def test_fetch_public_content():
    """Test the fetch_public_content function"""
    
    print("🧪 Testing fetch_public_content() module...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        "Bill Gates",
        "https://linkedin.com/in/satyanadella",
        "Elon Musk"
    ]
    
    for test_input in test_cases:
        print(f"\n📝 Testing with: {test_input}")
        print("-" * 30)
        
        try:
            updates = await fetch_public_content(test_input)
            
            print(f"✅ Found {len(updates)} updates")
            
            for i, update in enumerate(updates, 1):
                print(f"\n{i}. {update.get('source', 'Unknown')}")
                print(f"   Title: {update.get('title', 'No title')}")
                print(f"   Snippet: {update.get('snippet', 'No snippet')[:100]}...")
                print(f"   Date: {update.get('date', 'No date')}")
                print(f"   URL: {update.get('url', 'No URL')}")
            
            # Validate structure
            if updates:
                first_update = updates[0]
                required_keys = ['source', 'title', 'snippet', 'date', 'url']
                missing_keys = [key for key in required_keys if key not in first_update]
                
                if missing_keys:
                    print(f"❌ Missing required keys: {missing_keys}")
                else:
                    print("✅ All required keys present")
                    
                # Check snippet length
                if len(first_update.get('snippet', '')) < 20:
                    print("⚠️  Snippet might be too short")
                else:
                    print("✅ Snippet length is good")
            else:
                print("⚠️  No updates found (this might be expected for some names)")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_fetch_public_content()) 