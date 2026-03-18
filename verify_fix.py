import asyncio
import os
import sys

# Add current directory to path so we can import routes/utils
sys.path.append(os.getcwd())

# Mock the environment to test fallback
os.environ["GEMINI_API_KEY"] = ""
os.environ["GROQ_API_KEY"] = ""
os.environ["IBM_API_KEY"] = ""
os.environ["HF_API_KEY"] = ""

from routes.recommend import get_recommendations, RecommendRequest
from routes.analyze import analyze_person
from routes.stylist import chat_with_stylist, StylistRequest
from routes.trends import get_trends

async def test_fallbacks():
    print("Testing Fallbacks (Missing Keys)...")
    
    # Test Recommend
    try:
        req = RecommendRequest(body_type="Average", style_preference="Casual", occasion="Work")
        res = await get_recommendations(req)
        print(f"✅ Recommend fallback: SUCCESS (got {len(res['recommendations'])} recs)")
    except Exception as e:
        print(f"❌ Recommend fallback: FAILED ({str(e)})")

    # Test Trends
    try:
        res = await get_trends()
        print(f"✅ Trends fallback: SUCCESS (got {res['season']})")
    except Exception as e:
        print(f"❌ Trends fallback: FAILED ({str(e)})")

    # Test Stylist
    try:
        req = StylistRequest(message="What should I wear?")
        res = await chat_with_stylist(req)
        print(f"✅ Stylist fallback: SUCCESS (is_mock: {res.get('is_mock')})")
    except Exception as e:
        print(f"❌ Stylist fallback: FAILED ({str(e)})")

if __name__ == "__main__":
    asyncio.run(test_fallbacks())
