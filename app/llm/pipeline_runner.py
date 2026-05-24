from app.agents.research_agent import run_research_agent, format_research
from app.agents.writer_agent import run_writer_agent, format_blog
from app.agents.carousel_agent import run_carousel_agent, format_carousel
from app.agents.video_agent import run_video_agent, format_video

def initialize_state(
    source_text,
    pdf_paths,
    style_sample,
    channels,
    template_path,
    task_id=None
):
    import uuid
    return {
        "task_id": task_id or str(uuid.uuid4()),
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

async def run_agent_pipeline(
    source_text: str,
    pdf_paths: list[str],
    style_sample: str,
    channels: list,
    template_path: str = None,
    task_id: str = None
):
    state = initialize_state(
        source_text,
        pdf_paths,
        style_sample,
        channels,
        template_path,
        task_id
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
            "carousel": format_carousel(state["carousel"]["slides"], state["task_id"]) if state["carousel"]["slides"] else None,
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