import os
import json
import aiohttp
from dotenv import load_dotenv

load_dotenv()

_ibm_api_key = os.getenv("IBM_API_KEY", "")
_ibm_project_id = os.getenv("IBM_PROJECT_ID", "")

# IBM watsonx.ai endpoint
IBM_WX_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
IBM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

_cached_token = None


async def _get_iam_token(api_key: str) -> str:
    """Exchange IBM API key for IAM bearer token."""
    global _cached_token
    if _cached_token:
        return _cached_token
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                IBM_TOKEN_URL,
                data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    _cached_token = data.get("access_token")
                    return _cached_token
    except Exception:
        pass
    return None


async def generate_text_ibm(prompt: str, api_key: str = None, project_id: str = None) -> str:
    """Generate text using IBM Granite model via watsonx.ai."""
    key = api_key or _ibm_api_key
    pid = project_id or _ibm_project_id

    if not key or key == "your_ibm_api_key_here":
        return None

    token = await _get_iam_token(key)
    if not token:
        return None

    payload = {
        "model_id": "ibm/granite-13b-instruct-v2",
        "project_id": pid,
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 800,
            "temperature": 0.7
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                IBM_WX_URL,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    results = data.get("results", [])
                    if results:
                        return results[0].get("generated_text", "")
                return None
    except Exception as e:
        raise Exception(f"IBM watsonx error: {str(e)}")


def is_available(api_key: str = None) -> bool:
    key = api_key or _ibm_api_key
    return bool(key and key != "your_ibm_api_key_here")
