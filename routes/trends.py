from fastapi import APIRouter, Query
from typing import Optional
from utils import gemini_client

router = APIRouter()

MOCK_TRENDS = {
    "season": "Spring/Summer 2025",
    "headline": "The Era of Expressive Minimalism",
    "trends": [
        {
            "name": "Quiet Luxury 2.0",
            "description": "Elevated basics with impeccable tailoring — logo-free, quality-driven fashion that whispers rather than shouts.",
            "key_pieces": ["Cashmere sweaters", "Tailored trousers", "Leather loafers", "Silk scarves"],
            "colors": ["Ivory", "Camel", "Navy", "Forest Green"],
            "heat_level": "🔥🔥🔥🔥🔥"
        },
        {
            "name": "Neo-Preppy",
            "description": "Collegiate style gets a modern overhaul with bold colors and unexpected proportions.",
            "key_pieces": ["Varsity jackets", "Pleated skirts", "Argyle knits", "Chunky loafers"],
            "colors": ["Burgundy", "Forest Green", "Cream", "Navy"],
            "heat_level": "🔥🔥🔥🔥"
        },
        {
            "name": "Dopamine Dressing",
            "description": "Vibrant, mood-boosting colors and playful patterns that celebrate self-expression.",
            "key_pieces": ["Bright blazers", "Color-block sets", "Statement accessories", "Printed trousers"],
            "colors": ["Electric Blue", "Sunny Yellow", "Hot Pink", "Tangerine"],
            "heat_level": "🔥🔥🔥🔥"
        },
        {
            "name": "Gorpcore Revival",
            "description": "Outdoor functional wear infiltrates high fashion — utility meets style.",
            "key_pieces": ["Technical vests", "Cargo trousers", "Trail runners", "Fleece jackets"],
            "colors": ["Olive", "Sand", "Stone", "Rust"],
            "heat_level": "🔥🔥🔥"
        }
    ],
    "style_tip": "Mix trends intentionally — pair one statement piece with understated basics to look intentional rather than costume-y.",
    "must_have_accessory": "Oversized sunglasses — they elevate any outfit instantly and are universally flattering."
}

@router.get("/trends")
async def get_trends(
    season: Optional[str] = Query(default="current"),
    style: Optional[str] = Query(default="all"),
    api_key: Optional[str] = Query(default=None)
):
    prompt = f"""
You are StyleSense, a trend-forecasting AI with expertise in global fashion weeks and street style.

Provide the latest fashion trend report for {season} season, focusing on {style} style.

Include:
1. Season name and headline theme
2. 4 major trends with:
   - Trend name
   - Description (2 sentences)
   - Key pieces (4 items)
   - Associated colors (4 colors)
   - Heat level (🔥 to 🔥🔥🔥🔥🔥)
3. Overall styling tip for this season
4. Must-have accessory of the moment

Format as valid JSON:
{{
  "season": "...",
  "headline": "...",
  "trends": [
    {{
      "name": "...",
      "description": "...",
      "key_pieces": ["...", "..."],
      "colors": ["...", "..."],
      "heat_level": "🔥🔥🔥🔥"
    }}
  ],
  "style_tip": "...",
  "must_have_accessory": "..."
}}
"""
    result = await gemini_client.generate_text(prompt, api_key)

    if result is None:
        return MOCK_TRENDS

    try:
        import json, re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass

    return MOCK_TRENDS
