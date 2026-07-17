"""
app/services/gemini_client.py
==============================
Gemini LLM service wrapper for the ClimateSense AI Pipeline.

This module is the single integration point between the LangGraph nodes
(Recommendation Generator, Challenge Generator, Report Generator) and the
Gemini API. It owns:

- Loading configuration (API key, model name) from environment variables.
- A single, process-wide `genai.Client` instance (singleton — never
  recreated per call).
- A generic, resilient JSON-generation helper (`_generate_json`) with
  retries, markdown-fence stripping, and expected-field validation.
- Three narrow, purpose-built public functions that the nodes import
  directly: `generate_recommendations`, `generate_daily_challenge`, and
  `generate_report`.

Design notes
------------
* Uses the current `google-genai` SDK (`google.genai`), not the legacy
  `google.generativeai` package.
* All Gemini calls request `response_mime_type="application/json"` so the
  model returns structured output directly; `_clean_json_string` is kept
  as a defensive second layer in case the model still wraps output in
  markdown code fences.
* Every public function returns plain Python `dict`/`list[dict]` objects,
  which is exactly what the calling nodes expect: they take this raw data
  and construct their own Pydantic models (`Recommendation`, `EcoChallenge`,
  etc.) from it. This module intentionally has no dependency on
  `app.graph.state`, keeping the service layer decoupled from the graph
  schema.
* Function names are unchanged from the existing project so that no node
  or import needs to change: `generate_recommendations`,
  `generate_daily_challenge`, `generate_report`.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------

load_dotenv()

GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    _handler.setFormatter(_formatter)
    logger.addHandler(_handler)

if not GEMINI_API_KEY:
    logger.warning(
        "GEMINI_API_KEY is not set. Gemini API calls will fail until it is "
        "configured in the environment or a .env file."
    )

# ---------------------------------------------------------------------------
# Singleton Gemini client
# ---------------------------------------------------------------------------
# Constructed exactly once at import time and reused for every request.
# Never re-instantiate `genai.Client` inside a function.

client: Optional[genai.Client] = None
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as _client_init_error:  # noqa: BLE001 - defensive, logged below
    logger.error(
        f"Failed to construct Gemini client at import time: {_client_init_error}. "
        "Gemini calls will fail with a clear error until this is resolved."
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _clean_json_string(raw_text: str) -> str:
    """Strip markdown code fences and surrounding whitespace from model output.

    Gemini is instructed to return raw JSON, but this acts as a defensive
    second layer in case the model still wraps its output in a ```json
    ... ``` or ``` ... ``` fence.

    Args:
        raw_text: The raw text returned by the Gemini response.

    Returns:
        str: The cleaned string, ready to be passed to `json.loads`.
    """
    text = raw_text.strip()

    if text.startswith("```"):
        # Drop the opening fence line (``` or ```json).
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
        else:
            text = text.lstrip("`")

        # Drop a trailing fence if present.
        if text.rstrip().endswith("```"):
            text = text.rstrip()[: -3]

    return text.strip()


def _validate_fields(
    parsed_json: Union[Dict[str, Any], List[Dict[str, Any]]],
    expected_fields: List[str],
) -> bool:
    """Validate that parsed JSON contains all expected fields.

    Supports both a single JSON object and a list of JSON objects (each
    item in the list is validated independently).

    Args:
        parsed_json: The parsed JSON payload — either a dict or a list of dicts.
        expected_fields: Field names that must be present on every object.

    Returns:
        bool: True if all expected fields are present, False otherwise.
    """
    if isinstance(parsed_json, dict):
        return all(field in parsed_json for field in expected_fields)

    if isinstance(parsed_json, list):
        if not parsed_json:
            return False
        return all(
            isinstance(item, dict) and all(field in item for field in expected_fields)
            for item in parsed_json
        )

    return False


def _generate_json(
    prompt: str, expected_fields: List[str]
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Send a prompt to Gemini, enforce JSON output, validate, and parse it.

    Retries once on failure (two total attempts). Failure modes covered:
    empty responses, malformed JSON, and responses missing expected fields.

    Args:
        prompt: The user-facing prompt/instructions to send to Gemini.
        expected_fields: Field names that must be present in the parsed
            JSON response (validated on every object if a list is returned).

    Returns:
        Union[Dict[str, Any], List[Dict[str, Any]]]: The parsed and
        validated JSON response, as either a single object or a list of
        objects, depending on what Gemini returns.

    Raises:
        RuntimeError: If all attempts fail (empty response, invalid JSON,
            missing fields, or any other Gemini/client error).
    """
    strict_prompt = (
        f"{prompt}\n\n"
        "IMPORTANT:\n"
        "- Return ONLY valid JSON.\n"
        "- Do NOT wrap JSON inside markdown.\n"
        "- Do NOT include explanations.\n"
        "- Do NOT include code fences.\n"
        "- Output ONLY the requested JSON."
    )

    max_attempts = 2
    retry_delay_seconds = 2
    last_error: str = "Unknown error"

    if client is None:
        raise RuntimeError(
            "Gemini client is not initialized (GEMINI_API_KEY missing or invalid). "
            "Set GEMINI_API_KEY in your environment or .env file."
        )

    for attempt in range(1, max_attempts + 1):
        try:
            logger.info(f"Gemini request started (attempt {attempt}/{max_attempts}).")

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=strict_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )

            if response is None:
                raise RuntimeError("Gemini returned None.")

            if not hasattr(response, "text"):
                raise RuntimeError("Gemini response has no 'text' attribute.")

            if response.text is None or response.text.strip() == "":
                raise RuntimeError("Gemini returned an empty response.")

            raw_text = response.text.strip()
            logger.debug(f"Gemini raw response: {raw_text}")

            clean_text = _clean_json_string(raw_text)

            try:
                parsed_json = json.loads(clean_text)
            except json.JSONDecodeError as decode_error:
                raise RuntimeError(f"JSON Decode Error: {decode_error}") from decode_error

            if not _validate_fields(parsed_json, expected_fields):
                raise RuntimeError(
                    f"Gemini response missing one or more expected fields: {expected_fields}"
                )

            logger.info(f"Gemini request succeeded on attempt {attempt}/{max_attempts}.")
            return parsed_json

        except Exception as exc:
            last_error = str(exc)
            logger.warning(f"Gemini request attempt {attempt}/{max_attempts} failed: {last_error}")

            if attempt < max_attempts:
                logger.info(f"Retrying Gemini request in {retry_delay_seconds}s...")
                time.sleep(retry_delay_seconds)

    logger.error(f"Gemini request failed after {max_attempts} attempts. Reason: {last_error}")
    raise RuntimeError(
        f"Gemini request failed after {max_attempts} attempts. Reason: {last_error}"
    )


# ---------------------------------------------------------------------------
# Public API — consumed directly by the LangGraph nodes
# ---------------------------------------------------------------------------


def generate_recommendations(prompt: str) -> List[Dict[str, Any]]:
    """Generate a list of personalized sustainability recommendations.

    Consumed by `app.nodes.recommendation_generator.recommendation_generator_node`.

    Args:
        prompt: The fully constructed grounding prompt built by the
            Recommendation Generator node.

    Returns:
        List[Dict[str, Any]]: A list of recommendation objects, each with
        keys: `title`, `description`, `category`, `estimated_impact_kg_co2`,
        and `priority`.

    Raises:
        RuntimeError: If Gemini fails to produce a valid response after retries.
    """
    expected_fields = [
        "title",
        "description",
        "category",
        "estimated_impact_kg_co2",
        "priority",
    ]

    logger.info("Generating sustainability recommendations via Gemini.")
    result = _generate_json(prompt, expected_fields)

    if isinstance(result, dict):
        # Defensive normalization: some prompts may yield a single object
        # instead of a list; wrap it so callers can always iterate safely.
        return [result]

    return result


def generate_daily_challenge(prompt: str) -> Dict[str, Any]:
    """Generate exactly one personalized daily eco-challenge.

    Consumed by `app.nodes.challenge_generator.challenge_generator_node`.

    Args:
        prompt: The fully constructed grounding prompt built by the
            Challenge Generator node.

    Returns:
        Dict[str, Any]: A single challenge object with keys: `title`,
        `description`, `category`, `difficulty`, and
        `estimated_co2_savings_kg`.

    Raises:
        RuntimeError: If Gemini fails to produce a valid response after retries.
    """
    expected_fields = [
        "title",
        "description",
        "category",
        "difficulty",
        "estimated_co2_savings_kg",
    ]

    logger.info("Generating daily eco-challenge via Gemini.")
    result = _generate_json(prompt, expected_fields)

    if isinstance(result, list):
        if not result:
            raise RuntimeError("Gemini returned an empty list for the daily challenge.")
        # Defensive normalization: a single challenge is expected as a dict;
        # if the model returns a one-item list, unwrap it.
        return result[0]

    return result


def generate_report(prompt: str) -> Dict[str, Any]:
    """Generate the final sustainability report narrative.

    Consumed by `app.nodes.report_generator.report_generator_node`.

    Args:
        prompt: The fully constructed grounding prompt built by the
            Report Generator node.

    Returns:
        Dict[str, Any]: A report object with keys: `main_report`,
        `motivational_closing`, and `progress_summary`.

    Raises:
        RuntimeError: If Gemini fails to produce a valid response after retries.
    """
    expected_fields = ["main_report", "motivational_closing", "progress_summary"]

    logger.info("Generating final sustainability report via Gemini.")
    result = _generate_json(prompt, expected_fields)

    if isinstance(result, list):
        if not result:
            raise RuntimeError("Gemini returned an empty list for the sustainability report.")
        return result[0]

    return result