import os
from app.llm.model import creative_llm
from app.llm.prompts.designer_prompt import visual_designer_prompt
from app.schemas.outputs import carousel_parser
from app.agents.research_agent import format_research
from app.agents.writer_agent import format_blog
from app.services.image_generation import generate_carousel_images

def format_carousel(carousel_output, task_id: str = None) -> str:
    lines = ["# Carousel Slides\n"]
    for slide in carousel_output.slides:
        lines.append(f"### Slide {slide.slide_number}: {slide.title}")
        lines.append(f"**Overlay Text:** {slide.overlay_text}")
        lines.append(f"**Visual Direction:** {slide.visual_direction}")
        
        # Embed generated slide image if available
        if task_id:
            image_filename = f"slide_{task_id}_{slide.slide_number}.jpg"
            if os.path.exists(os.path.join("ui/generated", image_filename)):
                lines.append(f"\n![Slide {slide.slide_number} Image](/generated/{image_filename})")
                
        lines.append(f"\n**AI Image Prompt:** `{slide.image_prompt}`\n")
        lines.append("---")
    return "\n".join(lines)

async def run_carousel_agent(state):
    designer_chain = visual_designer_prompt | creative_llm | carousel_parser
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

    # Generate slide images concurrently in parallel
    state["logs"].append("Initiating parallel image generation...")
    image_logs = await generate_carousel_images(
        slides=result.slides,
        task_id=state["task_id"],
        template_path=state["input"]["template_path"]
    )
    for log in image_logs:
        state["logs"].append(log)
