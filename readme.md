# 🚀 Content Studio: Agentic Multi-Channel Content Engine
**Architectural Blueprint & User Guide**

Welcome to the **Agentic Multi-Channel Content Engine (Content Studio)**. Content Studio is an autonomous content orchestration system designed to ingest complex research documents (PDFs), visual template layouts, and text drafts to perform agent-based validation and generate ready-to-publish assets for multiple channels (Blog, Social Media Carousels, and Video).

---

## 🗺️ System Architecture

Content Studio is designed with a lightweight, high-performance architecture utilizing **FastAPI** to serve both the REST API and the Glassmorphism-style frontend, and **LangChain** to coordinate the multi-agent execution pipeline.

```mermaid
graph TD
    User([User / Creator]) -->|1. Uploads PDF & Image Template| UI[Custom Frontend UI]
    UI -->|2. POST /api/generate| API[FastAPI Backend]
    
    subgraph Agentic Orchestration [LangChain Pipeline]
        API -->|3. Runs Background Task| Runner[Pipeline Runner]
        Runner -->|4. Invokes Chain| Researcher[Researcher Agent Chain]
        Researcher -->|5. Context Fact-check| Writer[Writer Agent Chain]
        Writer -->|6. Polished Blog| Designer[Visual Designer Chain]
        Writer -->|7. Polished Blog| Director[Multimedia Director Chain]
    end

    subgraph LLM & Media Generation
        Researcher & Writer & Designer & Director -->|Prompts| GeminiLLM[Google Gemini LLM]
        Director -->|Returns| VideoURL[Video URL Asset]
    end

    Designer -->|8. Carousel Script| API
    Director -->|9. Video Script & Asset| API
    API -->|10. Poll /api/status| UI
```

---

## 🤖 Agentic Pipeline & Core Roles

The generation pipeline is built with sequential LangChain runnables, executing the following specialized personas in order:

| Agent Persona | Role | Primary Model | Input | Output |
| :--- | :--- | :--- | :--- | :--- |
| **Lead Researcher** | Fact-checking, source validation, and context extraction | `gemini-1.5-flash` | User raw text + PDF context | A structured summary of facts |
| **Content Architect** | Writing long-form blog posts matching a style tone sample | `gemini-1.5-flash` | Original draft + style sample + researcher report | A polished Markdown blog post |
| **Visual Strategist** | Designing slides and layouts for social media carousels | `gemini-1.5-flash` | Polished blog post + optional template path | Slide-by-slide titles and visual prompts |
| **Multimedia Director**| Scripting narration and providing video asset sequences | `gemini-1.5-flash` | Polished blog post | Narrator script synced with video stream URLs |

---

## 🔌 API Documentation

### 1. File Upload: `POST /api/upload`
Uploads PDFs or image templates to the local storage.
* **Request:** Multipart Form (`file`)
* **Response:**
  ```json
  { "pdf_path": "uploads/filename.ext" }
  ```

### 2. Generate Content: `POST /api/generate`
Triggers the background agent execution.
* **Request Schema:**
  ```json
  {
    "source_text": "string (optional draft)",
    "pdf_path": "string (optional uploaded PDF path)",
    "style_sample": "string (optional writing tone reference)",
    "channels": ["blog", "carousel", "video"],
    "template_path": "string (optional uploaded template image path)"
  }
  ```
* **Response Schema:**
  ```json
  {
    "task_id": "string (UUID)",
    "status": "pending"
  }
  ```

### 3. Execution Status: `GET /api/status/{task_id}`
Retrieves active agent execution progress and final generation assets.
* **Response Schema:**
  ```json
  {
    "task_id": "string",
    "status": "pending | processing | completed | failed",
    "current_agent": "Lead Researcher",
    "progress_percentage": 60,
    "artifacts": {
      "blog_post": "string (Markdown)",
      "carousel": "string (Carousel slides)",
      "video": {
        "script": "string (Video script)",
        "video_url": "string (MP4 stream URL)"
      }
    }
  }
  ```

---

## 🏃 Getting Started

### 1. Clone & Set Up Environment
Create a virtual environment and install the required dependencies:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start the Application
Run the FastAPI development server:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Open **http://127.0.0.1:8000** in your browser to view the interactive dashboard.