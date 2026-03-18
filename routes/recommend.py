from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from utils import gemini_client

router = APIRouter()

class RecommendRequest(BaseModel):
    body_type: str
    style_preference: str
    occasion: str
    color_palette: Optional[str] = "neutral"
    budget: Optional[str] = "mid-range"
    gender: Optional[str] = "unisex"
    season: Optional[str] = "all-season"
    api_key: Optional[str] = None

class OutfitItem(BaseModel):
    name: str
    description: str
    items: List[str]
    color_scheme: str
    styling_tips: str

class RecommendResponse(BaseModel):
    recommendations: List[dict]
    general_advice: str
    color_suggestions: str

MOCK_RECOMMENDATIONS = {
    "recommendations": [
        {
            "name": "Classic Casual Chic",
            "description": "A timeless, effortlessly stylish everyday look.",
            "items": ["White cotton button-down shirt", "Dark slim-fit jeans", "White leather sneakers", "Minimalist watch"],
            "color_scheme": "White, Indigo, Crisp Neutrals",
            "styling_tips": "Tuck in the front of the shirt for a polished yet relaxed vibe."
        },
        {
            "name": "Smart Business Casual",
            "description": "Professional yet approachable for office settings.",
            "items": ["Navy blazer", "Light grey trousers", "White dress shirt", "Brown leather loafers"],
            "color_scheme": "Navy, Grey, White",
            "styling_tips": "Roll up the blazer sleeves slightly for a modern touch."
        },
        {
            "name": "Weekend Relaxed",
            "description": "Comfortable and stylish for weekend outings.",
            "items": ["Oversized linen shirt", "Chino shorts", "Canvas slip-ons", "Straw hat"],
            "color_scheme": "Beige, Sand, Earth Tones",
            "styling_tips": "Layer with a light jacket for cooler evenings."
        }
    ],
    "shopping_items": [
        {"name": "White Cotton Button-Down", "query": "white cotton button down shirt"},
        {"name": "Dark Slim Jeans", "query": "dark slim jeans"},
        {"name": "Navy Blazer", "query": "navy blue blazer"}
    ],
    "general_advice": "Focus on fit first — well-fitted clothes always look more put-together regardless of price. Invest in quality basics that mix and match easily.",
    "color_suggestions": "Your palette works beautifully with earthy neutrals, classic navy, and crisp whites. Add a pop of color with accessories."
}

@router.post("/recommend")
async def get_recommendations(request: RecommendRequest):
    prompt = f"""
You are StyleSense, an expert AI fashion stylist. Create 3 personalized outfit recommendations for this person:

- Body Type: {request.body_type}
- Style Preference: {request.style_preference}
- Occasion: {request.occasion}
- Color Palette: {request.color_palette}
- Budget: {request.budget}
- Gender: {request.gender}
- Season: {request.season}

For each outfit provide:
1. Outfit name
2. Short description
3. Specific clothing items (list of 4-5 pieces)
4. Color scheme
5. Styling tips

Also provide:
- General fashion advice for this person
- Color combination suggestions

Format your response as valid JSON with this structure:
{{
  "recommendations": [
    {{
      "name": "...",
      "description": "...",
      "items": ["item1", "item2", ...],
      "color_scheme": "...",
      "styling_tips": "..."
    }}
  ],
  "general_advice": "...",
  "color_suggestions": "..."
}}
"""
    try:
        print(f"DEBUG: Generating recommendations for body_type={request.body_type}, style={request.style_preference}")
        result = await gemini_client.generate_text(prompt, request.api_key)
    except Exception as e:
        print(f"ERROR: Gemini recommendation failed: {str(e)}")
        result = None

    if result is None:
        print("DEBUG: Using mock recommendations (fallback)")
        # Return mock data when no API key or error
        return MOCK_RECOMMENDATIONS

    try:
        import json, re
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data
        else:
            raise ValueError("No JSON found")
    except Exception:
        # Fallback: return structured text
        return {
            "recommendations": [
                {"name": "AI Suggestion", "description": result[:300], "items": [], "color_scheme": "", "styling_tips": ""}
            ],
            "general_advice": "",
            "color_suggestions": ""
        }
