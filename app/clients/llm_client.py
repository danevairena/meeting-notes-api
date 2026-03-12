import json
from typing import Any

from google import genai
from google.genai import types
from google.genai import types as gemini_types
from openai import OpenAI
from pydantic import BaseModel

from app.settings import settings


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

# generate structured output for the selected llm provider
def generate_structured_content(llm: str, prompt: str, response_schema: type, temperature: float = 0) -> tuple[Any, str]:
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
def _generate_gemini_structured_content(prompt: str, response_schema: type, temperature: float = 0) -> tuple[Any, str]:
    response = _gemini_client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_schema,
        ),
    )

    parsed = response.parsed

    # fail fast when gemini does not return valid structured output
    if parsed is None:
        raise ValueError("gemini returned invalid structured output")

    raw_output = response.text or json.dumps(parsed.model_dump(), ensure_ascii=False)

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