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

MOCK_RECOMMENDATIONS_MALE = {
    "recommendations": [
        {
            "name": "Classic Casual Chic",
            "description": "A timeless, effortlessly stylish everyday look for men.",
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
        {"name": "White Cotton Button-Down", "query": "white cotton button down shirt for men"},
        {"name": "Dark Slim Jeans", "query": "dark slim jeans for men"},
        {"name": "Navy Blazer", "query": "navy blue blazer for men"}
    ],
    "general_advice": "Focus on fit first — well-fitted clothes always look more put-together regardless of price. Invest in quality basics that mix and match easily.",
    "color_suggestions": "Your palette works beautifully with earthy neutrals, classic navy, and crisp whites. Add a pop of color with accessories."
}

MOCK_RECOMMENDATIONS_FEMALE = {
    "recommendations": [
        {
            "name": "Sophisticated Everyday",
            "description": "A polished and versatile look for the modern woman.",
            "items": ["Silk midi skirt", "Fitted cashmere sweater", "Pointed-toe flats", "Gold hoop earrings"],
            "color_scheme": "Cream, Camel, Gold",
            "styling_tips": "Balance the flowy skirt with a structured bag for a professional edge."
        },
        {
            "name": "Chic City Style",
            "description": "Effortlessly cool for urban adventures and social gatherings.",
            "items": ["Straight-leg leather trousers", "Oversized white poplin shirt", "Strappy sandals", "Minimalist tote"],
            "color_scheme": "Black, White, Tan",
            "styling_tips": "Leave the shirt half-tucked to create a relaxed yet intentional silhouette."
        },
        {
            "name": "Elevated Casual Weekend",
            "description": "Comfort meets high-end style for relaxed outings.",
            "items": ["High-waisted linen trousers", "Ribbed tank top", "Denim jacket", "Leather slides"],
            "color_scheme": "Olive, White, Denim",
            "styling_tips": "Drape the denim jacket over your shoulders for a stylish, layered effect."
        }
    ],
    "shopping_items": [
        {"name": "Silk Midi Skirt", "query": "silk midi skirt for women"},
        {"name": "Cashmere Sweater", "query": "cashmere sweater for women"},
        {"name": "Leather Trousers", "query": "leather trousers for women"}
    ],
    "general_advice": "Accessorizing is the key to personalizing your look. A statement belt or unique jewelry can completely transform simple silhouettes.",
    "color_suggestions": "Soft earth tones and classic neutrals provide a timeless foundation. Experiment with jewel-toned accents for a sophisticated pop."
}

@router.post("/recommend")
async def get_recommendations(request: RecommendRequest):
    prompt = f"""
You are StyleSense, an expert AI fashion stylist. Create 3 personalized outfit recommendations for this {request.gender.upper()} person:

Target Gender: {request.gender.upper()} (IMPORTANT: Ensure all clothing items and descriptions are for {request.gender})

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
        print(f"DEBUG: Using gender-specific mock recommendations for {request.gender}")
        # Return mock data when no API key or error
        return MOCK_RECOMMENDATIONS_FEMALE if request.gender == "female" else MOCK_RECOMMENDATIONS_MALE

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
