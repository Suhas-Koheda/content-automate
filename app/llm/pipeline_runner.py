import os
from typing import List, Optional
from pydantic import BaseModel
from app.llm.model import llm
from app.llm.prompts.research_prompt import researcher_prompt
from app.llm.prompts.designer_prompt import visual_designer_prompt
from app.llm.prompts.multimedia_prompt import multimedia_prompt
from app.llm.prompts.writer_prompt import writer_prompt
from app.utils.pdf_reader import extract_text_from_pdf, extract_text_from_pdfs
from langchain_core.output_parsers import PydanticOutputParser

# Pydantic Schemas for Structured Agent Outputs
class ResearchOutput(BaseModel):
    summary: str
    key_claims: List[str]
    sources_used: List[str]

class WriterOutput(BaseModel):
    title: str
    blog_markdown: str

class Slide(BaseModel):
    slide_number: int
    title: str
    overlay_text: str
    image_prompt: str
    visual_direction: str

class CarouselOutput(BaseModel):
    slides: List[Slide]

class Scene(BaseModel):
    scene_number: int
    visual_description: str
    audio_dialogue: str
    timing: str

class VideoOutput(BaseModel):
    scenes: List[Scene]

# Output Parsers
research_parser = PydanticOutputParser(pydantic_object=ResearchOutput)
writer_parser = PydanticOutputParser(pydantic_object=WriterOutput)
carousel_parser = PydanticOutputParser(pydantic_object=CarouselOutput)
video_parser = PydanticOutputParser(pydantic_object=VideoOutput)

# Helper Formatters to convert Pydantic Models to Strings for Prompts/Frontend
def format_research(report: ResearchOutput) -> str:
    lines = [f"# Research Summary\n{report.summary}\n", "## Key Claims"]
    for claim in report.key_claims:
        lines.append(f"- {claim}")
    lines.append("\n## Sources Used")
    for source in report.sources_used:
        lines.append(f"- {source}")
    return "\n".join(lines)

def format_blog(writer_output: WriterOutput) -> str:
    return f"# {writer_output.title}\n\n{writer_output.blog_markdown}"

def format_carousel(carousel_output: CarouselOutput) -> str:
    lines = ["# Carousel Slides\n"]
    for slide in carousel_output.slides:
        lines.append(f"### Slide {slide.slide_number}: {slide.title}")
        lines.append(f"**Overlay Text:** {slide.overlay_text}")
        lines.append(f"**Visual Direction:** {slide.visual_direction}")
        lines.append(f"**AI Image Prompt:** `{slide.image_prompt}`\n")
        lines.append("---")
    return "\n".join(lines)

def format_video(video_output: VideoOutput) -> str:
    lines = ["# Video Script & Storyboard\n"]
    for scene in video_output.scenes:
        lines.append(f"### Scene {scene.scene_number} ({scene.timing})")
        lines.append(f"**Visual Description:** {scene.visual_description}")
        lines.append(f"**Audio/Voiceover:** *{scene.audio_dialogue}*\n")
        lines.append("---")
    return "\n".join(lines)

def initialize_state(
    source_text,
    pdf_paths,
    style_sample,
    channels,
    template_path
):
    return {
        "input": {
            "source_text": source_text,
            "pdf_paths": pdf_paths,
            "style_sample": style_sample,
            "channels": channels,
            "template_path": template_path
        },

        "context": {
            "documents": [],
            "template_metadata": {}
        },

        "research": {
            "status": "pending",
            "output": None
        },

        "writer": {
            "status": "pending",
            "blog": None
        },

        "carousel": {
            "status": "pending",
            "slides": None
        },

        "video": {
            "status": "pending",
            "script": None,
            "video_url": None
        },

        "logs": [],
        "errors": []
    }

async def run_research_agent(state):
    pdf_paths = state["input"]["pdf_paths"]
    pdf_text = extract_text_from_pdfs(pdf_paths)
    state["context"]["documents"].append({
        "type": "pdf_collection",
        "paths": pdf_paths,
        "text": pdf_text
    })
    
    research_chain = researcher_prompt | llm | research_parser
    result = await research_chain.ainvoke({
        "source_text": state["input"]["source_text"] or "No draft text provided.",
        "pdf_context": "\n".join(
            doc["text"]
            for doc in state["context"]["documents"]
        ) or "No PDF context provided.",
        "format_instructions": research_parser.get_format_instructions()
    })
    state["research"]["status"] = "completed"
    state["research"]["output"] = result
    state["logs"].append("Research agent completed")

async def run_writer_agent(state):
    writer_chain = writer_prompt | llm | writer_parser
    result = await writer_chain.ainvoke({
        "draft_blog": state["input"]["source_text"] or "No draft text provided.",
        "style_sample": state["input"]["style_sample"] or "No style sample provided.",
        "research_report": format_research(state["research"]["output"]),
        "format_instructions": writer_parser.get_format_instructions()
    })
    state["writer"]["status"] = "completed"
    state["writer"]["blog"] = result
    state["logs"].append("Writer agent completed")

async def run_carousel_agent(state):
    designer_chain = visual_designer_prompt | llm | carousel_parser
    result = await designer_chain.ainvoke({
        "source_text": state["input"]["source_text"] or "No draft text provided.",
        "research_report": format_research(state["research"]["output"]),
        "blog_post": format_blog(state["writer"]["blog"]),
        "style_sample": state["input"]["style_sample"] or "No style sample provided.",
        "pdf_context": "\n".join(
            doc["text"]
            for doc in state["context"]["documents"]
        ) or "No PDF context provided.",
        "template_reference": (
            state["input"]["template_path"]
            or "No template provided"
        ),
        "format_instructions": carousel_parser.get_format_instructions()
    })
    state["carousel"]["status"] = "completed"
    state["carousel"]["slides"] = result
    state["logs"].append("Carousel agent completed")

async def run_video_agent(state):
    video_chain = multimedia_prompt | llm | video_parser
    result = await video_chain.ainvoke({
        "research_data": format_blog(state["writer"]["blog"]),
        "format_instructions": video_parser.get_format_instructions()
    })
    state["video"]["status"] = "completed"
    state["video"]["script"] = result
    state["logs"].append("Video agent completed")

async def run_agent_pipeline(
    source_text: str,
    pdf_paths: list[str],
    style_sample: str,
    channels: list,
    template_path: str = None
):
    state = initialize_state(
        source_text,
        pdf_paths,
        style_sample,
        channels,
        template_path
    )

    try:
        await run_research_agent(state)

        await run_writer_agent(state)

        if "carousel" in channels:
            await run_carousel_agent(state)

        if "video" in channels:
            await run_video_agent(state)

        return {
            "blog_post": format_blog(state["writer"]["blog"]) if state["writer"]["blog"] else None,
            "carousel": format_carousel(state["carousel"]["slides"]) if state["carousel"]["slides"] else None,
            "video": {
                "script": format_video(state["video"]["script"]) if state["video"]["script"] else None,
                "video_url": state["video"]["video_url"]
            },
            "logs": state["logs"]
        }

    except Exception as e:
        state["errors"].append(str(e))
        return {
            "error": str(e),
            "logs": state["logs"]
        }