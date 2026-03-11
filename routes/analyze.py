from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from utils import gemini_client
from utils import groq_client
from utils import hf_client
from utils import ibm_client

router = APIRouter()

# Mock data for demo mode
MOCK_RESULT = {
    "skin_tone": {
        "category": "Medium",
        "hex": "#C68642",
        "rgb": {"r": 198, "g": 134, "b": 66},
        "undertone": "Warm",
        "description": "You have a beautiful medium warm skin tone with golden undertones — similar to celebrities like Jennifer Lopez and Priyanka Chopra."
    },
    "dress_code": ["Formal", "Business", "Casual", "Party"],
    "suggested_outfit": "A navy blue suit with a white dress shirt, paired with dark brown chinos and loafers, perfect for formal events, while a more casual look could include a light grey polo shirt with dark jeans and sneakers for everyday wear.",
    "clothing_items": [
        {"item": "Shirt", "color": "Light Grey", "type": "Polo", "brand": "Calvin Klein", "fabric": "Cotton"},
        {"item": "Pant", "color": "Dark Brown", "type": "Chinos", "brand": "Bonobos", "fabric": "Cotton"},
        {"item": "Shoes", "color": "Tan", "type": "Loafers", "brand": "Gucci", "fabric": "Leather"}
    ],
    "hairstyle": {
        "style": "Fade with Pompadour",
        "how_to": "Start by cutting the sides and back with a fade technique, then use pomade to style the top hair into a pompadour, finishing with a light hold hairspray. For daily maintenance, reapply pomade as needed and trim the edges every two weeks."
    },
    "accessories": ["Leather Watch", "Simple Silver Necklace", "Brown Leather Belt", "Aviator Sunglasses"],
    "color_palette": {
        "primary": "Navy Blue",
        "secondary": "Light Grey",
        "accent": "Tan"
    },
    "why_it_works": "The recommended color palette works perfectly for your skin tone — navy blue and light grey create a harmonious contrast, while tan accents complement your natural undertones beautifully.",
    "style_vibe": ["Casual", "Business"],
    "shopping_items": [
        {"name": "Navy Blue Suit", "query": "navy blue suit men"},
        {"name": "Light Grey Polo Shirt", "query": "light grey polo shirt"},
        {"name": "Dark Brown Chinos", "query": "dark brown chinos men"},
        {"name": "Tan Leather Loafers", "query": "tan leather loafers men"},
        {"name": "Leather Watch", "query": "men leather watch"},
        {"name": "Burgundy Loafers", "query": "burgundy loafers men"}
    ]
}


def _build_style_prompt(gender: str, skin_category: str, undertone: str, hex_code: str) -> str:
    return f"""You are StyleSense, an expert AI fashion stylist. Generate a comprehensive personalized style profile for a {gender} with:

Skin Tone: {skin_category}
Undertone: {undertone}
Hex: {hex_code}

Provide SPECIFIC brand names, colors, and fabrics. Return ONLY valid JSON in this EXACT format:
{{
  "dress_code": ["Formal", "Business", "Casual", "Party"],
  "suggested_outfit": "A detailed 2-sentence outfit description with specific colors and pieces.",
  "clothing_items": [
    {{"item": "Shirt", "color": "...", "type": "...", "brand": "...", "fabric": "..."}},
    {{"item": "Pant", "color": "...", "type": "...", "brand": "...", "fabric": "..."}},
    {{"item": "Shoes", "color": "...", "type": "...", "brand": "...", "fabric": "..."}}
  ],
  "hairstyle": {{
    "style": "Hairstyle name",
    "how_to": "Step-by-step 3-4 sentence guide with maintenance tips."
  }},
  "accessories": ["Accessory 1", "Accessory 2", "Accessory 3", "Accessory 4"],
  "color_palette": {{
    "primary": "Color name",
    "secondary": "Color name",
    "accent": "Color name"
  }},
  "why_it_works": "A 3-4 sentence explanation of why this palette complements their skin tone.",
  "shopping_items": [
    {{"name": "Item name", "query": "amazon search query for {gender}"}},
    {{"name": "Item name", "query": "amazon search query for {gender}"}},
    {{"name": "Item name", "query": "amazon search query for {gender}"}},
    {{"name": "Item name", "query": "amazon search query for {gender}"}},
    {{"name": "Item name", "query": "amazon search query for {gender}"}}
  ]
}}
Return only valid JSON. No markdown, no explanation."""


def _parse_json(text: str) -> dict | None:
    if not text:
        return None
    try:
        import json, re
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception:
        pass
    return None


@router.post("/analyze")
async def analyze_person(
    file: UploadFile = File(...),
    gender: Optional[str] = Form(default="male"),
    gemini_key: Optional[str] = Form(default=None),
    groq_key: Optional[str] = Form(default=None),
    hf_token: Optional[str] = Form(default=None),
    ibm_key: Optional[str] = Form(default=None),
    ibm_project_id: Optional[str] = Form(default=None),
):
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted.")

    image_data = await file.read()

    # ── Step 1: Skin tone detection via Gemini Vision ──────────────────
    vision_prompt = f"""Analyze this person's photo carefully. Detect their skin tone precisely.
Gender: {gender}

Return ONLY a JSON with this exact format:
{{
  "skin_tone_category": "Light/Medium-Light/Medium/Medium-Deep/Deep",
  "hex_code": "#C68642",
  "rgb": {{"r": 198, "g": 134, "b": 66}},
  "undertone": "Warm/Cool/Neutral",
  "description": "A warm personal 1-sentence description of their unique skin tone"
}}
Return only JSON, no other text."""

    skin_result = await gemini_client.analyze_image_with_text(image_data, vision_prompt, gemini_key)
    skin_data = _parse_json(skin_result)

    if skin_data is None:
        skin_data = {
            "skin_tone_category": "Medium",
            "hex_code": "#C68642",
            "rgb": {"r": 198, "g": 134, "b": 66},
            "undertone": "Warm",
            "description": "You have a beautiful medium warm skin tone with radiant golden undertones."
        }

    skin_category = skin_data.get("skin_tone_category", "Medium")
    undertone = skin_data.get("undertone", "Warm")
    hex_code = skin_data.get("hex_code", "#C68642")

    style_prompt = _build_style_prompt(gender, skin_category, undertone, hex_code)

    # ── Step 2: Style generation — cascade through AI providers ───────
    # Try Groq first (fastest), then IBM, then HF, then Gemini, then mock
    style_data = None
    ai_provider_used = "demo"

    # 2a. Groq (primary — fast)
    if style_data is None:
        try:
            result = await groq_client.generate_text_groq(style_prompt, groq_key)
            style_data = _parse_json(result)
            if style_data:
                ai_provider_used = "groq"
        except Exception:
            pass

    # 2b. IBM watsonx (secondary)
    if style_data is None:
        try:
            result = await ibm_client.generate_text_ibm(style_prompt, ibm_key, ibm_project_id)
            style_data = _parse_json(result)
            if style_data:
                ai_provider_used = "ibm"
        except Exception:
            pass

    # 2c. Hugging Face (tertiary)
    if style_data is None:
        try:
            result = await hf_client.query_hf_text(
                "mistralai/Mistral-7B-Instruct-v0.3", style_prompt, hf_token
            )
            style_data = _parse_json(result)
            if style_data:
                ai_provider_used = "huggingface"
        except Exception:
            pass

    # 2d. Gemini text (quaternary)
    if style_data is None:
        try:
            result = await gemini_client.generate_text(style_prompt, gemini_key)
            style_data = _parse_json(result)
            if style_data:
                ai_provider_used = "gemini"
        except Exception:
            pass

    # 2e. Demo fallback
    if style_data is None:
        style_data = {k: MOCK_RESULT[k] for k in MOCK_RESULT if k != "skin_tone"}
        ai_provider_used = "demo"

    # ── Step 3: HF style vibe classification (bonus enrichment) ───────
    style_vibe = []
    if hf_client.is_available(hf_token):
        try:
            outfit_text = style_data.get("suggested_outfit", "")
            hf_result = await hf_client.analyze_sentiment_hf(outfit_text, hf_token)
            if hf_result and "labels" in hf_result:
                style_vibe = hf_result["labels"][:3]
        except Exception:
            pass

    return {
        "skin_tone": {
            "category": skin_data.get("skin_tone_category", "Medium"),
            "hex": skin_data.get("hex_code", "#C68642"),
            "rgb": skin_data.get("rgb", {"r": 198, "g": 134, "b": 66}),
            "undertone": skin_data.get("undertone", "Warm"),
            "description": skin_data.get("description", "")
        },
        "ai_provider": ai_provider_used,
        "style_vibe": style_vibe,
        **style_data
    }
