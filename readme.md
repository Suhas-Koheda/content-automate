# content-engine

A lightweight FastAPI application for ingesting and processing assets (PDFs, images, videos, text) with LLM-powered prompt templates.

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your LLM API keys:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run the FastAPI server:

```bash
uvicorn main:app --reload
```

## Project Structure

- `main.py` — FastAPI app with `/ingest` endpoint
- `models/` — Pydantic models for assets and outputs
  - `Asset.py` — Input asset schema
  - `Processed_Assests.py` — Processed asset containers
  - `llm_output.py` — LLM output schemas
- `utils/Ingestor.py` — Asset processing (OCR, text extraction, PDF handling)
- `llm/` — LLM integration
  - `llm.py` — LLM client and model definitions
  - `prompts/` — Prompt templates (research, writer, designer, multimedia)

## Usage

POST a list of assets to `/ingest`:

```json
[
  {"id":"1","type":"document","path":"/path/to/doc.pdf"},
  {"id":"2","type":"image","path":"/path/to/image.jpg"},
  {"id":"3","type":"text","content":"Some text content"}
]
```

Supported asset types: `image`, `video`, `document`, `text`

The endpoint returns a `ProcessedAssets` object containing extracted text, images, and document metadata.
