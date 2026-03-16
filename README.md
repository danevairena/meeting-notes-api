# Meeting Notes API

FastAPI backend for uploading meeting transcripts, storing them in Supabase, chunking long transcripts, and generating structured meeting notes with an LLM.

The project supports transcript ingestion from **`.docx` and `.pdf` files**, stores raw transcripts and transcript chunks, and exposes REST endpoints for creating projects, creating meetings, uploading files, processing meetings, and fetching generated notes.

---

## Features

- FastAPI REST API
- Upload transcripts from `.docx` and `.pdf`
- Parse meeting title and date from file names
- Store projects, meetings, transcript chunks, and notes in Supabase
- Chunk long transcripts before LLM processing
- Generate structured notes with **Gemini** or **OpenAI**
- Cache recent processing results in memory
- Rate-limit repeated processing calls per meeting and LLM
- Return consistent API error responses
- SQL migration for initial PostgreSQL schema

---

## Tech Stack

- Python
- FastAPI
- Supabase / PostgreSQL
- Google Gemini SDK
- OpenAI SDK
- Pydantic
- python-docx
- pypdf
- pytest

---

## Project Structure

```text
meeting-notes-api
├── app
│   ├── clients
│   │   ├── __init__.py
│   │   ├── llm_client.py
│   │   └── supabase_client.py
│   │
│   ├── migrations
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_llm_column_to_notes.sql
│   │   ├── 003_add_google_docs_source_fields_to_meetings.sql
│   │   └── 004_allow_null_source_file.sql
│   │
│   ├── models
│   │   ├── __init__.py
│   │   ├── error.py
│   │   ├── google_docs_import.py
│   │   ├── meeting.py
│   │   ├── note.py
│   │   ├── processing.py
│   │   └── project.py
│   │
│   ├── repositories
│   │   ├── __init__.py
│   │   ├── chunks_repository.py
│   │   ├── meetings_repository.py
│   │   ├── notes_repository.py
│   │   └── projects_repository.py
│   │
│   ├── routers
│   │   ├── __init__.py
│   │   ├── meetings.py
│   │   └── projects.py
│   │
│   ├── services
│   │   ├── __init__.py
│   │   ├── chunks_service.py
│   │   ├── file_extraction_service.py
│   │   ├── google_docs_import_service.py
│   │   ├── llm_extraction_service.py
│   │   ├── meetings_service.py
│   │   ├── notes_service.py
│   │   ├── process_cache_service.py
│   │   ├── processing_service.py
│   │   ├── projects_service.py
│   │   └── upload_meeting_service.py
│   │
│   ├── utils
│   │   ├── chunking.py
│   │   ├── docx_reader.py
│   │   ├── google_docs.py
│   │   ├── parsing.py
│   │   └── pdf_reader.py
|   |
│   ├── __init__.py
│   ├── errors.py
│   ├── logging_config.py
│   ├── main.py
│   └── settings.py
│
├── tests
│   ├── conftest.py
│   ├── test_google_docs_utils.py
│   ├── test_health.py
│   └── test_meetings.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Architecture

The application follows a layered backend structure:

### 1. Routers
Expose the HTTP API and validate request/response shapes.

### 2. Services
Contain business logic such as:
- meeting creation
- file upload handling
- transcript extraction
- chunking
- LLM processing
- caching and rate limiting

### 3. Repositories
Handle database reads/writes against Supabase tables.

### 4. Clients
Wrap external integrations:
- Supabase client
- Gemini client
- OpenAI client

### 5. Utils
Provide reusable transcript-processing helpers:
- DOCX reader
- PDF reader
- filename parsing
- chunking

---

## How the Processing Flow Works

### Upload flow

1. Client uploads a `.docx` or `.pdf` file.
2. The file is temporarily stored.
3. The filename is parsed for metadata.
4. Transcript text is extracted from the file.
5. A project is resolved or created.
6. A meeting row is created in the database.

### Processing flow

1. The meeting transcript is loaded from the database.
2. The transcript is split into chunks.
3. Existing transcript chunks for the meeting are replaced.
4. Each chunk is sent to the selected LLM.
5. Chunk-level notes are merged.
6. A final summary is generated.
7. Notes are rewritten to reduce duplication.
8. Final notes are saved in the `notes` table.
9. The result is cached in memory.

---

## API Endpoints

Base URL for local development:

```bash
http://localhost:8000
```

### Health

#### `GET /health`

Checks whether the service is running.

Example:

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "ok",
  "environment": "development"
}
```

---

### Projects

#### `GET /projects/`

Returns all projects.

```bash
curl http://localhost:8000/projects/
```

#### `GET /projects/{project_id}`

Returns a single project.

```bash
curl http://localhost:8000/projects/<project_id>
```

#### `POST /projects/`

Creates a project.

```bash
curl -X POST http://localhost:8000/projects/   -H "Content-Type: application/json"   -d '{
    "name": "AI Platform"
  }'
```

Example response:

```json
{
  "id": "uuid",
  "name": "AI Platform",
  "created_at": "2026-03-12T10:00:00+00:00"
}
```

---

### Meetings

#### `GET /meetings/`

Returns all meetings.

```bash
curl http://localhost:8000/meetings/
```

Filter by project:

```bash
curl "http://localhost:8000/meetings/?project_id=<project_id>"
```

#### `GET /meetings/{meeting_id}`

Returns a single meeting.

```bash
curl http://localhost:8000/meetings/<meeting_id>
```

#### `GET /meetings/{meeting_id}/notes`

Returns all generated note versions for a meeting.

```bash
curl http://localhost:8000/meetings/<meeting_id>/notes
```

#### `GET /meetings/{meeting_id}/chunks`

Returns stored transcript chunks for a meeting.

```bash
curl http://localhost:8000/meetings/<meeting_id>/chunks
```

#### `POST /meetings/`

Creates a meeting directly from JSON.

```bash
curl -X POST http://localhost:8000/meetings/   -H "Content-Type: application/json"   -d '{
    "title": "Weekly Sync",
    "meeting_date": "2026-03-10",
    "source": "manual",
    "source_file": "weekly-sync-march-10.docx",
    "raw_transcript": "Full transcript text goes here.",
    "project_id": null
  }'
```

#### `POST /meetings/upload`

Uploads a transcript file and creates a meeting from it.

```bash
curl -X POST http://localhost:8000/meetings/upload   -F "file=@./sample-meeting.docx"   -F "source=upload"   -F "project_name=AI Platform"
```

Notes:
- Supported file types: `.docx`, `.pdf`
- If `project_name` is empty, the service falls back to `"unknown"`

#### `POST /meetings/{meeting_id}/process`

Processes a meeting with the selected LLM.

```bash
curl -X POST http://localhost:8000/meetings/<meeting_id>/process   -H "Content-Type: application/json"   -d '{
    "llm": "gemini"
  }'
```

Process with OpenAI:

```bash
curl -X POST http://localhost:8000/meetings/<meeting_id>/process   -H "Content-Type: application/json"   -d '{
    "llm": "openai"
  }'
```

Example response shape:

```json
{
  "id": "uuid",
  "meeting_id": "uuid",
  "summary": "The team reviewed current priorities and agreed on next steps.",
  "action_items": [
    {
      "task": "Prepare revised roadmap",
      "owner": "Irena",
      "due_date": null
    }
  ],
  "key_takeaways": [
    {
      "text": "Roadmap updates are needed before the next review."
    }
  ],
  "topics": [
    {
      "name": "Roadmap planning"
    }
  ],
  "next_steps": [
    {
      "step": "Share the updated roadmap draft",
      "owner": "Irena",
      "due_date": null
    }
  ],
  "llm_raw": "..."
}
```
#### `POST /meetings/import/google-docs`

Imports multiple meetings from public Google Docs.

Each provided Google Doc is downloaded, converted to plain text, and stored as a meeting transcript.

```bash
curl -X POST http://localhost:8000/meetings/import/google-docs \
  -H "Content-Type: application/json" \
  -d '{
    "meetings": [
      {
        "title": "Sprint Planning",
        "google_doc_url": "https://docs.google.com/document/d/GOOGLE_DOC_ID/edit"
      },
      {
        "title": "Retrospective",
        "google_doc_url": "https://docs.google.com/document/d/GOOGLE_DOC_ID/edit"
      }
    ]
  }'
```

### Response example

``` json
{
  "total": 2,
  "imported": 1,
  "failed": 1,
  "results": [
    {
      "title": "Sprint Planning",
      "status": "imported",
      "meeting_id": "uuid"
    },
    {
      "title": "Retrospective",
      "status": "failed",
      "error": "Document not accessible"
    }
  ]
}
```

The endpoint processes each document independently.\
If one document fails, the others can still be imported.

---

### How it works

1.  The API extracts the Google Doc ID from the provided URL.
2.  The document is downloaded using the Google Docs export endpoint.
3.  The document is converted to plain text.
4.  The text is stored in the `raw_transcript` field.
5.  A meeting record is created with:

-   `source = "google_docs"`
-   `source_url`
-   `external_id`
-   `raw_transcript`

---

### Limitations

-   Only **public Google Docs** are supported.
-   Private documents requiring authentication cannot be imported.
-   Documents are imported as **plain text**, formatting is not
    preserved.
-   The meeting date defaults to the current date if not provided.

---

### How to test

1.  Create a public Google Doc.
2.  Add some meeting notes text.
3.  Copy the document URL.
4.  Send a request to:

```{=html}
<!-- -->
```
    POST /meetings/import/google-docs

Example using curl:

``` bash
curl -X POST http://localhost:8000/meetings/import/google-docs -H "Content-Type: application/json" -d '{
  "meetings": [
    {
      "title": "Team Sync",
      "google_doc_url": "https://docs.google.com/document/d/DOC_ID/edit"
    }
  ]
}'
```

---

## Request and Response Models

### `MeetingCreate`

```json
{
  "title": "Weekly Sync",
  "meeting_date": "2026-03-10",
  "source": "manual",
  "source_file": "weekly-sync.docx",
  "raw_transcript": "Transcript text",
  "project_id": null
}
```

### `ProcessMeetingRequest`

```json
{
  "llm": "gemini"
}
```

Accepted values in the current implementation:
- `gemini`
- `openai`

### `ProjectCreate`

```json
{
  "name": "AI Platform"
}
```

### Standard error response

```json
{
  "error": "bad_request",
  "message": "only .docx and .pdf files are supported"
}
```

---

## LLM Extraction Strategy

The pipeline uses two stages of LLM work:

### 1. Chunk extraction
Each transcript chunk is converted into structured notes with:
- summary
- action items
- key takeaways
- topics
- next steps

### 2. Final cleanup
After all chunks are processed:
- summaries are merged
- one final summary is generated
- notes are rewritten to remove duplicates and noise

This is implemented for both:
- Gemini
- OpenAI

---

## Chunking Strategy

Long transcripts are split with overlap before being sent to the LLM.

Default chunking parameters:

- `chunk_size = 1200`
- `overlap = 150`

The chunker also tries to stop chunks near sentence boundaries when possible.

---

## File Parsing Rules

When a meeting is uploaded, the filename parser tries to extract meeting metadata from names like:

```text
AI TEAM MEETING - July 17 (37 mins).docx
```

Parsed fields:
- title
- meeting date
- optional duration in minutes

If parsing fails:
- the file stem becomes the title
- the file modification date becomes the meeting date

If the parsed date would be in the future, the parser shifts it to the previous year.

---

## Database Schema

The repository includes `app/migrations/`
- `001_initial_schema.sql`
- `002_add_llm_to_notes.sql`

These migrations define the PostgreSQL schema used by the application.

The database is hosted in Supabase (PostgreSQL).

### `projects`

| column | type |
|---|---|
| id | uuid |
| name | text |
| created_at | timestamptz |

### `meetings`

| column | type |
|---|---|
| id | uuid |
| project_id | uuid |
| title | text |
| meeting_date | date |
| source | text |
| source_file | text |
| raw_transcript | text |
| created_at | timestamptz |

Indexes:
- unique index on `source_file` - prevents duplicate ingestion of the same meeting file
- index on `(project_id, meeting_date)` - speeds up project meeting queries

### `notes`

| column | type |
|---|---|
| id | uuid |
| meeting_id | uuid |
| llm | text |
| summary | text |
| action_items | jsonb |
| key_takeaways | jsonb |
| topics | jsonb |
| next_steps | jsonb |
| llm_raw | text |
| created_at | timestamptz |

- `unique(meeting_id, llm)` - This ensures that each LLM can generate only one note version per meeting.

### `transcript_chunks`

| column | type |
|---|---|
| id | uuid |
| meeting_id | uuid |
| chunk_index | int |
| content | text |
| created_at | timestamptz |

Constraints:
- unique `(meeting_id, chunk_index)`

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/danevairena/meeting-notes-api.git
cd meeting-notes-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**macOS / Linux**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

The repo includes `.env.example` with:

```env
APP_ENV=development
APP_NAME=Meeting Notes API
APP_VERSION=0.1.0
SUPABASE_URL=
SUPABASE_KEY=
GEMINI_API_KEY=
LOG_LEVEL=INFO
```

The settings module also supports these additional values:

```env
GEMINI_MODEL=gemini-2.0-flash
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

### 5. Run the SQL migration

Apply:

```sql
app/migrations/001_initial_schema.sql
```

to your Supabase/PostgreSQL database.

### 6. Start the API

```bash
uvicorn app.main:app --reload
```

---

## Running Tests

Run the test suite with:

```bash
pytest
```

At the moment, the repository contains:
- `test_health.py`
- `test_meetings.py`
- `conftest.py`

`test_health.py` contains a working health-check test.

---

## Example Workflow

### 1. Create a project

```bash
curl -X POST http://localhost:8000/projects/   -H "Content-Type: application/json"   -d '{"name":"AI Platform"}'
```

### 2. Upload a transcript

```bash
curl -X POST http://localhost:8000/meetings/upload   -F "file=@./AI TEAM MEETING - July 17 (37 mins).docx"   -F "source=upload"   -F "project_name=AI Platform"
```

### 3. Process the meeting with Gemini

```bash
curl -X POST http://localhost:8000/meetings/<meeting_id>/process   -H "Content-Type: application/json"   -d '{"llm":"gemini"}'
```

### 4. Fetch generated notes

```bash
curl http://localhost:8000/meetings/<meeting_id>/notes
```

---

## Current Limitations

- Processing cache is in-memory only, so it resets on application restart.
- Rate limiting is in-memory only.
- Test coverage is still minimal.
- There is no background job queue; processing happens during the request.
- Duplicate meeting protection depends on the `source_file` unique index.

---

## Author

**Irena Daneva**  
GitHub: `danevairena`

---

## Project Purpose

This project is a backend portfolio project focused on:

- API design with FastAPI
- layered backend architecture
- file ingestion and parsing
- Supabase/PostgreSQL persistence
- transcript chunking
- structured LLM extraction
- practical handling of caching, rate limiting, and error responses

It is a strong foundation for extending into:
- meeting intelligence products
- internal knowledge extraction tools
- searchable transcript systems
- multi-provider LLM experimentation
