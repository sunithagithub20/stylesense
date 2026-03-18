from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from utils import gemini_client

router = APIRouter()

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class StylistRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    api_key: Optional[str] = None

MOCK_RESPONSES = [
    "Great question! Based on general styling principles, I'd recommend starting with well-fitted basics in neutral tones — navy, white, grey, and beige. These form a versatile capsule wardrobe that mixes and matches effortlessly.",
    "For that occasion, I'd suggest a smart casual approach — think tailored chinos, a quality knit sweater, and clean white sneakers or loafers. It's polished without being overdressed.",
    "Color is such a powerful styling tool! A good rule of thumb: stick to 3 colors max per outfit. Pair neutrals with one accent color for a harmonious, intentional look.",
    "Accessories can truly elevate any outfit. A quality leather bag, a classic watch, or a silk scarf can transform basics into a complete, styled look.",
    "My top tip? Invest in fit. A well-tailored $30 shirt will always look better than an ill-fitting $300 one. When in doubt, visit a tailor!"
]

_mock_counter = 0

@router.post("/stylist")
async def chat_with_stylist(request: StylistRequest):
    global _mock_counter

    # Build conversation context
    system_prompt = """You are StyleSense AI Stylist — a warm, knowledgeable, and encouraging personal fashion advisor. 
You have deep expertise in:
- Personal styling and body-type dressing
- Color theory and palette matching  
- Current fashion trends and timeless classics
- Budget-friendly fashion tips
- Sustainable and ethical fashion

Respond in a conversational, friendly tone. Be specific and actionable. Keep responses concise (2-3 paragraphs max).
Always encourage the user's personal style journey."""

    history_text = ""
    if request.history:
        for msg in request.history[-6:]:  # Last 6 messages for context
            role = "You" if msg.role == "assistant" else "User"
            history_text += f"{role}: {msg.content}\n"

    full_prompt = f"{system_prompt}\n\nConversation history:\n{history_text}\nUser: {request.message}\n\nYour response:"

    try:
        print(f"DEBUG: Chatting with stylist - message: {request.message[:50]}...")
        result = await gemini_client.generate_text(full_prompt, request.api_key)
    except Exception as e:
        print(f"ERROR: Gemini stylist chat failed: {str(e)}")
        result = None

    if result is None:
        print("DEBUG: Using mock stylist response (fallback)")
        response = MOCK_RESPONSES[_mock_counter % len(MOCK_RESPONSES)]
        _mock_counter += 1
        return {"response": response, "is_mock": True}

    return {"response": result, "is_mock": False}
