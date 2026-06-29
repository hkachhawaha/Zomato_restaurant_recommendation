import json
import time
import asyncio
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types
from google.genai.errors import APIError
from zomato_ai.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key: str = settings.GEMINI_API_KEY):
        self.api_key = api_key
        self.client_initialized = False
        self.client = None
        
        if self.api_key and self.api_key.strip():
            try:
                # Initialize the modern google-genai Client with attempts=1 to disable internal retries and a strict timeout
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options=types.HttpOptions(
                        timeout=30.0,
                        retry_options=types.HttpRetryOptions(attempts=1)
                    )
                )
                self.client_initialized = True
            except Exception as e:
                logger.error(f"Failed to configure Gemini Developer SDK Client: {e}")

    async def get_recommendations_with_reasoning(
        self, 
        prompt: str,
        retries: int = 2,
        backoff_factor: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Sends the candidate prompt to Gemini 2.5 Flash, parses JSON results, and executes exponential backoff.
        Raises RuntimeError if LLM communication is unconfigured or breaks after retries.
        """
        if not self.client_initialized or not self.client:
            raise RuntimeError("Gemini Client is unconfigured. Missing GEMINI_API_KEY in .env.")

        # System prompt setting the behavior and persona rules
        system_instruction = (
            "You are an expert foodie concierge matching users with restaurant recommendations.\n"
            "Your objective is to analyze the candidate restaurants and recommend them to the user.\n"
            "Rules:\n"
            "1. Recommend ALL restaurants from the provided Candidate List that match the user's preferences. Do not arbitrarily exclude or drop any candidates. If the preferred cuisine is 'Any Cuisine' or not specified, the user is requesting a general recommendation; in this case, recommend a broad and diverse set of high-quality options from the list (at least 8-12 restaurants if they fit budget and rating) to provide a rich variety of choices.\n"
            "2. Provide a personalized \"ai_explanation\" for each restaurant. Explain why it matches the user's preferences (such as cuisine if specified, budget, rating, and any additional vibe constraints).\n"
            "3. Keep the tone friendly, helpful, and concise.\n"
            "4. Return output strictly as a JSON array."
        )

        # Configure response schemas and properties (low temperature, strict JSON enforcement)
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.2
        )
        
        for attempt in range(retries):
            try:
                # Query Gemini Developer API asynchronously in a threadpool to prevent blocking the event loop
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=config
                )
                
                # Check response payload
                if not response.text:
                    raise APIError("Empty text payload returned from Gemini API.")
                
                # Parse JSON array response
                try:
                    data = json.loads(response.text)
                    if isinstance(data, list):
                        return data
                    if isinstance(data, dict) and "recommendations" in data:
                        return data["recommendations"]
                    raise ValueError("JSON output did not match a structured list array shape.")
                except (json.JSONDecodeError, ValueError) as json_err:
                    logger.warning(f"Failed to parse JSON response on attempt {attempt + 1}: {json_err}. Raw: {response.text}")
                    raise APIError(f"Invalid JSON format returned: {json_err}")
                    
            except (APIError, Exception) as api_err:
                err_str = str(api_err).upper()
                is_fail_fast_error = (
                    "RESOURCE_EXHAUSTED" in err_str or 
                    "429" in err_str or 
                    "QUOTA" in err_str or
                    "503" in err_str or
                    "UNAVAILABLE" in err_str or
                    "TEMPORARY" in err_str
                )
                
                logger.warning(f"Gemini API request failed on attempt {attempt + 1}/{retries}: {api_err}")
                
                if is_fail_fast_error:
                    logger.warning("Gemini API rate limit, quota, or 503 unavailable error. Failing fast to trigger heuristic fallback.")
                    raise RuntimeError(f"Gemini API Quota/Service Unavailable: {api_err}")
                
                if attempt == retries - 1:
                    # Terminal retry attempt failed, propagate error to fallback handler
                    raise RuntimeError(f"Gemini API execution failed after {retries} retries: {api_err}")
                
                # Wait with exponential backoff
                wait_time = backoff_factor ** (attempt + 1)
                logger.info(f"Retrying request in {wait_time:.2f} seconds...")
                await asyncio.sleep(wait_time)
                
        raise RuntimeError("LLM request failed after execution pipeline retries.")
