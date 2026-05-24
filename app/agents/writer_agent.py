from app.llm.model import pro_llm
from app.llm.prompts.writer_prompt import writer_prompt
from app.schemas.outputs import writer_parser
from app.agents.research_agent import format_research

def format_blog(writer_output) -> str:
    markdown = writer_output.blog_markdown.strip()
    if markdown.startswith("#"):
        return markdown
    return f"# {writer_output.title}\n\n{markdown}"

async def run_writer_agent(state):
    writer_chain = writer_prompt | pro_llm | writer_parser
    result = await writer_chain.ainvoke({
        "draft_blog": state["input"]["source_text"] or "No draft text provided.",
        "style_sample": state["input"]["style_sample"] or "No style sample provided.",
        "research_report": format_research(state["research"]["output"]),
        "format_instructions": writer_parser.get_format_instructions()
    })
    state["writer"]["status"] = "completed"
    state["writer"]["blog"] = result
    state["logs"].append("Writer agent completed")
