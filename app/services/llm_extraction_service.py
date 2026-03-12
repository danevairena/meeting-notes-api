import json

from pydantic import BaseModel, Field, ConfigDict

from app.clients.llm_client import generate_structured_content, generate_text_content


# represent a single extracted action item
class ExtractedActionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    owner: str | None
    due_date: str | None


# represent a single extracted next step
class ExtractedNextStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    owner: str | None


# represent extracted meeting notes for a single transcript chunk
class ExtractedMeetingNotes(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    action_items: list[ExtractedActionItem]
    key_takeaways: list[str]
    topics: list[str]
    next_steps: list[ExtractedNextStep]


# represent rewritten clean meeting notes
class CleanMeetingNotes(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    summary: str
    action_items: list[ExtractedActionItem]
    key_takeaways: list[str]
    topics: list[str]
    next_steps: list[ExtractedNextStep]


# define prompt for chunk level extraction
PROMPT = """
Extract structured meeting notes from the transcript.

Return structured data following this schema:

{
  "summary": string,
  "action_items": [
    { "text": string, "owner": string | null, "due_date": string | null }
  ],
  "key_takeaways": [string],
  "topics": [string],
  "next_steps": [
    { "text": string, "owner": string | null }
  ]
}

Rules:
- Do not invent information
- If owner is unknown, use null
- If due_date is unknown, use null
- Summary should be concise and accurate
- Remove duplicate action items
- If the transcript is very short or unclear, return empty lists
"""


# define prompt for final summary generation
FINAL_SUMMARY_PROMPT = """
You are given multiple partial summaries from different chunks of the same meeting.

Write one final clean meeting summary in 3 to 5 sentences.

Rules:
- combine overlapping information
- remove repetition
- keep only the most important points
- do not invent information
- return plain text only
"""


# define prompt for cleaning merged notes
REWRITE_PROMPT = """
You are refining structured meeting notes.

You will receive meeting notes that were automatically extracted from a transcript.
They may contain duplicated information, overly detailed items, or loosely defined tasks.

Return the output using the same JSON schema:

{
  "summary": string,
  "action_items": [
    { "text": string, "owner": string | null, "due_date": string | null }
  ],
  "key_takeaways": [string],
  "topics": [string],
  "next_steps": [
    { "text": string, "owner": string | null }
  ]
}

Rules:
- do not invent information
- do not remove valid tasks
- preserve important names, numbers and decisions
- remove duplicates and near-duplicates
- keep wording simple and direct
- return only valid json
"""


# extract structured notes from a transcript chunk using the selected llm
def extract_notes_from_chunk(
    transcript: str,
    llm: str,
) -> tuple[dict[str, object], str]:
    prompt = f"{PROMPT}\n\nTranscript:\n{transcript}"

    parsed, raw_output = generate_structured_content(
        llm=llm,
        prompt=prompt,
        response_schema=ExtractedMeetingNotes,
    )

    return parsed.model_dump(), raw_output


# generate one final summary from multiple chunk summaries using the selected llm
def generate_final_summary(
    summaries: list[str],
    llm: str,
) -> str:
    cleaned_summaries = [summary.strip() for summary in summaries if summary.strip()]

    # return empty summary when there are no usable chunk summaries
    if not cleaned_summaries:
        return ""

    prompt = (
        f"{FINAL_SUMMARY_PROMPT}\n\n"
        f"Chunk summaries:\n" + "\n".join(f"- {summary}" for summary in cleaned_summaries)
    )

    return generate_text_content(
        llm=llm,
        prompt=prompt,
    )


# rewrite merged notes to remove duplication and noise using the selected llm
def rewrite_notes(
    notes: dict[str, object],
    llm: str,
) -> tuple[dict[str, object], str]:
    raw_input = json.dumps(notes, ensure_ascii=False, indent=2)
    prompt = f"{REWRITE_PROMPT}\n\nMeeting notes:\n{raw_input}"

    parsed, raw_output = generate_structured_content(
        llm=llm,
        prompt=prompt,
        response_schema=CleanMeetingNotes,
    )

    return parsed.model_dump(), raw_output