import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_groq_key = os.getenv("GROQ_API_KEY", "")
_client = None
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1200
TEMPERATURE = 0.7

def configure_groq(api_key: str = None):
    global _client, _groq_key
    key = api_key or _groq_key
    if key and key != "your_groq_api_key_here":
        _client = Groq(api_key=key)
        _groq_key = key
        return True
    return False

def get_groq_client():
    global _client
    if _client is None:
        configure_groq()
    return _client

async def generate_text_groq(prompt: str, api_key: str = None) -> str:
    if api_key:
        configure_groq(api_key)
    client = get_groq_client()
    if client is None:
        return None
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")
