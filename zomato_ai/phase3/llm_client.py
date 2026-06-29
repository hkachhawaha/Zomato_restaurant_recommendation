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
                # Initialize the google-genai Client with default timeout settings
                self.client = genai.Client(
                    api_key=self.api_key
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
        Sends the candidate prompt to Gemini, parses JSON results, and executes exponential backoff.
        Uses gemini-2.0-flash for speed; falls back to heuristics on failure.
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
            "4. Return output strictly as a JSON array of objects with keys: name, cuisine, rating, approx_cost, Location, ai_explanation."
        )

        # Configure response (low temperature, strict JSON enforcement)
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.2
        )
        
        # Try models in order; quotas are per-model so fallbacks have independent limits.
        model_candidates = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash-8b",
        ]
        last_error: Exception | None = None

        for model_name in model_candidates:
            for attempt in range(retries):
                try:
                    logger.info(f"Sending request to {model_name} (attempt {attempt + 1}/{retries})...")

                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=model_name,
                        contents=prompt,
                        config=config
                    )

                    if not response.text:
                        raise ValueError("Empty text payload returned from Gemini API.")

                    try:
                        data = json.loads(response.text)
                        if isinstance(data, list):
                            logger.info(f"Successfully received {len(data)} recommendations from {model_name}.")
                            return data
                        if isinstance(data, dict) and "recommendations" in data:
                            logger.info(f"Successfully received {len(data['recommendations'])} recommendations from {model_name}.")
                            return data["recommendations"]
                        raise ValueError("JSON output did not match a structured list array shape.")
                    except (json.JSONDecodeError, ValueError) as json_err:
                        logger.warning(f"Failed to parse JSON response on attempt {attempt + 1}: {json_err}. Raw: {response.text[:500]}")
                        raise ValueError(f"Invalid JSON format returned: {json_err}")

                except (APIError, Exception) as api_err:
                    err_str = str(api_err).upper()
                    is_quota_error = (
                        "RESOURCE_EXHAUSTED" in err_str or
                        "429" in err_str or
                        "QUOTA" in err_str
                    )
                    is_fatal_error = (
                        "503" in err_str or
                        "UNAVAILABLE" in err_str or
                        "PERMISSION_DENIED" in err_str or
                        "INVALID_API_KEY" in err_str or
                        "API_KEY_INVALID" in err_str
                    )

                    logger.warning(f"Gemini API [{model_name}] failed on attempt {attempt + 1}/{retries}: {api_err}")
                    last_error = api_err

                    if is_quota_error:
                        # Quota exhausted for this model — try the next one.
                        logger.warning(f"Quota exhausted for {model_name}. Trying next model.")
                        break

                    if is_fatal_error:
                        raise RuntimeError(f"Gemini API error: {api_err}")

                    if attempt == retries - 1:
                        # All retries for this model failed with a transient error; try next model.
                        logger.warning(f"All retries failed for {model_name}. Trying next model.")
                        break

                    wait_time = backoff_factor ** (attempt + 1)
                    logger.info(f"Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)

        raise RuntimeError(f"All Gemini models exhausted their quota or failed. Last error: {last_error}")

