import json
from typing import Any
import logging
from google import genai
from google.genai import types
from openai import OpenAI
from pydantic import BaseModel
from google.genai import errors as genai_errors

from openai import BadRequestError, RateLimitError
from app.settings import settings


logger = logging.getLogger(__name__)

# create provider clients once for the whole app
_gemini_client = genai.Client(api_key=settings.gemini_api_key)
_openai_client = OpenAI(api_key=settings.openai_api_key)

# validate supported llm providers early
def validate_llm_provider(llm: str) -> None:
    supported_llms = {"gemini", "openai"}

    if llm not in supported_llms:
        raise ValueError(f"unsupported llm provider: {llm}")

# return the configured model name for a given provider
def get_model_name(llm: str) -> str:
    validate_llm_provider(llm)

    if llm == "gemini":
        return settings.gemini_model

    if llm == "openai":
        return settings.openai_model

    raise ValueError(f"unsupported llm provider: {llm}")

# recursively set additionalProperties to false for all object schemas
def enforce_strict_json_schema(schema: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(schema, dict):
        return schema

    # make every object schema strict for openai structured outputs
    if schema.get("type") == "object":
        schema["additionalProperties"] = False

    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for value in properties.values():
            if isinstance(value, dict):
                enforce_strict_json_schema(value)

    items = schema.get("items")
    if isinstance(items, dict):
        enforce_strict_json_schema(items)

    for key in ("anyOf", "oneOf", "allOf"):
        value = schema.get(key)
        if isinstance(value, list):
            for sub_schema in value:
                if isinstance(sub_schema, dict):
                    enforce_strict_json_schema(sub_schema)

    defs = schema.get("$defs", {})
    if isinstance(defs, dict):
        for value in defs.values():
            if isinstance(value, dict):
                enforce_strict_json_schema(value)

    return schema

# generate structured output for the selected llm provider
def generate_structured_content(
    llm: str,
    prompt: str,
    response_schema: type[BaseModel],
    temperature: float = 0,
) -> tuple[Any, str]:
    validate_llm_provider(llm)

    if llm == "gemini":
        return _generate_gemini_structured_content(
            prompt=prompt,
            response_schema=response_schema,
            temperature=temperature,
        )

    if llm == "openai":
        return _generate_openai_structured_content(
            prompt=prompt,
            response_schema=response_schema,
            temperature=temperature,
        )

    raise ValueError(f"unsupported llm provider: {llm}")

# generate plain text output for the selected llm provider
def generate_text_content(llm: str, prompt: str, temperature: float = 0) -> str:
    validate_llm_provider(llm)

    if llm == "gemini":
        return _generate_gemini_text_content(
            prompt=prompt,
            temperature=temperature,
        )

    if llm == "openai":
        return _generate_openai_text_content(
            prompt=prompt,
            temperature=temperature,
        )

    raise ValueError(f"unsupported llm provider: {llm}")

# generate structured json output with gemini using pydantic schema
def _generate_gemini_structured_content(
    prompt: str,
    response_schema: type[BaseModel],
    temperature: float = 0,
) -> tuple[Any, str]:
    json_schema = response_schema.model_json_schema()
    json_schema = remove_additional_properties(json_schema)

    try:
        response = _gemini_client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
                response_json_schema=json_schema,
            ),
        )
    except genai_errors.APIError as e:
        logger.error("GEMINI API ERROR code=%s message=%s", e.code, e.message)
        if hasattr(e, "response"):
            logger.error("GEMINI RESPONSE: %s", e.response)
        logger.error("GEMINI SCHEMA: %s", json.dumps(json_schema, ensure_ascii=False))
        raise

    raw_output = (response.text or "").strip()

    if not raw_output:
        raise ValueError("gemini returned empty structured output")

    try:
        parsed = response_schema.model_validate_json(raw_output)
    except Exception as exc:
        logger.error("GEMINI RAW OUTPUT: %s", raw_output)
        raise ValueError("gemini returned invalid structured output") from exc

    return parsed, raw_output

# generate plain text with gemini
def _generate_gemini_text_content(prompt: str, temperature: float = 0) -> str:
    response = _gemini_client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
        ),
    )

    return (response.text or "").strip()

# generate structured json output with openai using json schema
def _generate_openai_structured_content(
    prompt: str,
    response_schema: type[BaseModel],
    temperature: float = 0,
) -> tuple[Any, str]:
    schema_name = response_schema.__name__
    json_schema = response_schema.model_json_schema()
    json_schema = enforce_strict_json_schema(json_schema)

    try:
        response = _openai_client.responses.create(
            model=settings.openai_model,
            input=prompt,
            temperature=temperature,
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": json_schema,
                    "strict": True,
                }
            },
        )

    except RateLimitError as e:
        logger.error("OPENAI RATE LIMIT: %s", e)
        if hasattr(e, "response") and e.response:
            logger.error("OPENAI RESPONSE BODY: %s", e.response.text)
        raise

    except BadRequestError as e:
        logger.error("OPENAI BAD REQUEST: %s", e)
        if hasattr(e, "response") and e.response:
            logger.error("OPENAI RESPONSE BODY: %s", e.response.text)
        raise

    raw_output = (response.output_text or "").strip()

    # fail fast when openai does not return structured output
    if not raw_output:
        raise ValueError("openai returned empty structured output")

    try:
        parsed_dict = json.loads(raw_output)
        parsed = response_schema.model_validate(parsed_dict)
    except Exception as exc:
        raise ValueError("openai returned invalid structured output") from exc

    return parsed, raw_output

# generate plain text with openai
def _generate_openai_text_content(
    prompt: str,
    temperature: float = 0,
) -> str:
    response = _openai_client.responses.create(
        model=settings.openai_model,
        input=prompt,
        temperature=temperature,
    )

    return (response.output_text or "").strip()

def remove_additional_properties(schema: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(schema, dict):
        return schema

    schema.pop("additionalProperties", None)
    schema.pop("additional_properties", None)

    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for value in properties.values():
            if isinstance(value, dict):
                remove_additional_properties(value)

    items = schema.get("items")
    if isinstance(items, dict):
        remove_additional_properties(items)

    for key in ("anyOf", "oneOf", "allOf"):
        value = schema.get(key)
        if isinstance(value, list):
            for sub_schema in value:
                if isinstance(sub_schema, dict):
                    remove_additional_properties(sub_schema)

    defs = schema.get("$defs", {})
    if isinstance(defs, dict):
        for value in defs.values():
            if isinstance(value, dict):
                remove_additional_properties(value)

    return schema