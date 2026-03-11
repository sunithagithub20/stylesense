import os
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

_hf_token = os.getenv("HF_API_TOKEN", "")

# Hugging Face Inference API endpoint
HF_API_URL = "https://api-inference.huggingface.co"


async def query_hf_text(model: str, inputs: str, token: str = None) -> dict:
    """Call Hugging Face Inference API for text generation."""
    key = token or _hf_token
    headers = {}
    if key and key != "your_hf_token_here":
        headers["Authorization"] = f"Bearer {key}"

    url = f"{HF_API_URL}/models/{model}"
    payload = {
        "inputs": inputs,
        "parameters": {"max_new_tokens": 800, "temperature": 0.7, "return_full_text": False}
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if isinstance(result, list) and result:
                        return result[0].get("generated_text", "")
                    return str(result)
                return None
    except Exception as e:
        raise Exception(f"Hugging Face API error: {str(e)}")


async def analyze_sentiment_hf(text: str, token: str = None) -> dict:
    """Use Hugging Face for fashion sentiment/vibe analysis."""
    key = token or _hf_token
    headers = {}
    if key and key != "your_hf_token_here":
        headers["Authorization"] = f"Bearer {key}"

    # Use a zero-shot classification model
    url = f"{HF_API_URL}/models/facebook/bart-large-mnli"
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": ["formal", "casual", "streetwear", "luxury", "sporty", "bohemian", "minimalist"]
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                return None
    except Exception as e:
        return None


def is_available(token: str = None) -> bool:
    key = token or _hf_token
    return bool(key and key != "your_hf_token_here")
