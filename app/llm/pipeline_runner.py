import os
from app.llm.model import llm
from app.llm.prompts.research_prompt import researcher_prompt
from app.llm.prompts.designer_prompt import visual_designer_prompt
from app.llm.prompts.multimedia_prompt import multimedia_prompt
from app.llm.prompts.writer_prompt import writer_prompt
from app.utils.pdf_reader import extract_text_from_pdf
from langchain_core.output_parsers import StrOutputParser

async def run_agent_pipeline(source_text: str, pdf_path: str, style_sample: str, channels: list, template_path: str = None) -> dict:
    # 1. Read PDF text if a path is provided
    pdf_context = ""
    if pdf_path and os.path.exists(pdf_path):
        pdf_context = extract_text_from_pdf(pdf_path)

    # 2. Run the Researcher Agent
    research_chain = researcher_prompt | llm | StrOutputParser()
    research_data = await research_chain.ainvoke({
        "source_text": source_text or "",
        "pdf_context": pdf_context
    })

    # Run the Writer Chain
    writer_chain = writer_prompt | llm | StrOutputParser()
    final_blog = await writer_chain.ainvoke({
        "draft_blog": source_text or "",
        "style_sample": style_sample or "",
        "research_report": research_data
    })

    artifacts = {
        "blog_post": final_blog
    }

    # 3. Conditionally run other agents based on selected channels
    if "carousel" in channels:
        designer_chain = visual_designer_prompt | llm | StrOutputParser()
        artifacts["carousel"] = await designer_chain.ainvoke({"research_data": final_blog})
        
    if "video" in channels:
        multimedia_chain = multimedia_prompt | llm | StrOutputParser()
        video_script = await multimedia_chain.ainvoke({"research_data": final_blog})
        artifacts["video"] = {
            "script": video_script,
            "video_url": "https://www.w3schools.com/html/mov_bbb.mp4"
        }

    return artifacts

    