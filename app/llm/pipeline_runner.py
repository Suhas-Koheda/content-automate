import os
from app.llm.model import llm
from app.llm.prompts.research_prompt import researcher_prompt
from app.llm.prompts.designer_prompt import visual_designer_prompt
from app.llm.prompts.multimedia_prompt import multimedia_prompt
from app.llm.prompts.writer_prompt import writer_prompt
from app.utils.pdf_reader import extract_text_from_pdf,extract_text_from_pdfs
from langchain_core.output_parsers import PydanticOutputParser
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
    pdf_paths=state["input"]["pdf_paths"]
    pdf_text=extract_text_from_pdfs(pdf_paths)
    state["context"]["documents"].append({
    "type": "pdf_collection",
    "paths": pdf_paths,
    "text": pdf_text
    })
    research_chain=researcher_prompt|llm|PydanticOutputParser()
    result=await research_chain.ainvoke({
        "source_text":state["input"]["source_text"],
        "pdf_context":"\n".join(
            doc["text"]
            for doc in state["context"]["documents"]
        )
    })
    state["research"]["status"]="completed"
    state["research"]["output"]=result
    state["logs"].append("Research agent completed")

async def run_writer_agent(state):
    writer_chain=writer_prompt|llm|PydanticOutputParser()
    result = await writer_chain.ainvoke({
        "draft_blog": state["input"]["source_text"] or "",
        "style_sample": state["input"]["style_sample"] or "",
        "research_report": state["research"]["output"]
    })
    state["writer"]["status"]="completed"
    state["writer"]["blog"]=result
    state["logs"].append("Writer agent completed")

async def run_carousel_agent(state):
    designer_chain=visual_designer_prompt|llm|PydanticOutputParser()
    result = await designer_chain.ainvoke({

    "source_text": state["input"]["source_text"],

    "research_report": state["research"]["output"],

    "blog_post": state["writer"]["blog"],

    "style_sample": state["input"]["style_sample"],

    "pdf_context": "\n".join(
        doc["text"]
        for doc in state["context"]["documents"]
    ),

    "template_reference": (
        state["input"]["template_path"]
        or "No template provided"
    )
    })
    state["carousel"]["status"]="completed"
    state["carousel"]["slides"]=result
    state["logs"].append("Carousel agent completed")

async def run_video_agent(state):
    video_chain=multimedia_prompt|llm|PydanticOutputParser()
    result = await video_chain.ainvoke({
        "research_data": state["writer"]["blog"]
    })
    state["video"]["status"]="completed"
    state["video"]["script"]=result
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
            "blog_post": state["writer"]["blog"],
            "carousel": state["carousel"]["slides"],
            "video": {
                "script": state["video"]["script"],
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