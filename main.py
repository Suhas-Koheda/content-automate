import asyncio
import os
import shutil
import uuid

from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.llm.pipeline_runner import run_agent_pipeline
from app.models.generation import GenerationRequest, GenerationResponse
from app.models.status import StatusResponse

tasks_db = {}

async def run_generation_execution(task_id: str, request: GenerationRequest):
    try:
        tasks_db[task_id]["status"] = "processing"
        tasks_db[task_id]["current_agent"] = "Lead Researcher"
        tasks_db[task_id]["progress_percentage"] = 20
        
        results = await run_agent_pipeline(
            source_text=request.source_text,
            pdf_paths=request.pdf_paths,
            style_sample=request.style_sample,
            channels=request.channels,
            template_path=request.template_path,
            task_id=task_id
        )
        
        if "error" in results:
            tasks_db[task_id]["status"] = "failed"
            tasks_db[task_id]["current_agent"] = None
            tasks_db[task_id]["progress_percentage"] = 100
            tasks_db[task_id]["artifacts"] = results
        else:
            tasks_db[task_id]["status"] = "completed"
            tasks_db[task_id]["current_agent"] = None
            tasks_db[task_id]["progress_percentage"] = 100
            tasks_db[task_id]["artifacts"] = results
    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["current_agent"] = None
        tasks_db[task_id]["progress_percentage"] = 100
        tasks_db[task_id]["artifacts"] = {"error": str(e)}


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path

ALLOWED_TYPES = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg"
]

@app.post("/api/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    os.makedirs("uploads", exist_ok=True)
    file_paths = []

    for file in files:
        # Validate MIME type
        if file.content_type not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} is not allowed. Supported formats: PDF, PNG, JPEG."
            )

        # Clean/sanitize filename to prevent directory traversal
        safe_filename = Path(file.filename).name
        if not safe_filename or safe_filename in [".", ".."]:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename."
            )

        file_path = os.path.join("uploads", safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_paths.append(file_path)

    return {"pdf_paths": file_paths}
@app.post("/api/generate", response_model=GenerationResponse)
async def generate(request: GenerationRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {
        "status": "pending",
        "progress_percentage": 0,
        "artifacts": {}
    }
    background_tasks.add_task(run_generation_execution, task_id, request)
    return GenerationResponse(task_id=task_id, status="pending")

@app.get("/api/status/{task_id}", response_model=StatusResponse)
async def get_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = tasks_db[task_id]
    return StatusResponse(
        task_id=task_id,
        status=task_data["status"],
        current_agent=task_data.get("current_agent"),
        progress_percentage=task_data["progress_percentage"],
        artifacts=task_data["artifacts"]
    )

os.makedirs("ui", exist_ok=True)

app.mount("/", StaticFiles(directory="ui", html=True), name="ui")
