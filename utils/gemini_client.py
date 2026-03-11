import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

_api_key = os.getenv("GEMINI_API_KEY", "")
_client = None

def configure(api_key: str = None):
    global _client, _api_key
    key = api_key or _api_key
    if key and key != "your_gemini_api_key_here":
        _client = genai.Client(api_key=key)
        _api_key = key
        return True
    return False

def get_client():
    global _client
    if _client is None:
        configure()
    return _client

async def analyze_image_with_text(image_data: bytes, prompt: str, api_key: str = None) -> str:
    if api_key:
        configure(api_key)
    client = get_client()
    if client is None:
        return None
    try:
        import PIL.Image, io
        img = PIL.Image.open(io.BytesIO(image_data))
        # Convert PIL image to bytes for the new SDK
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        image_bytes = buf.getvalue()

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                prompt,
            ],
        )
        return response.text
    except Exception as e:
        raise Exception(f"Gemini Vision error: {str(e)}")

async def generate_text(prompt: str, api_key: str = None) -> str:
    if api_key:
        configure(api_key)
    client = get_client()
    if client is None:
        return None
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")
