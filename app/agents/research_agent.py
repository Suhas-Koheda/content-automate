from app.llm.model import fast_llm
from app.llm.prompts.research_prompt import researcher_prompt
from app.schemas.outputs import research_parser
from app.utils.pdf_reader import extract_text_from_pdfs

def format_research(report) -> str:
    lines = [f"# Research Summary\n{report.summary}\n", "## Key Claims"]
    for claim in report.key_claims:
        lines.append(f"- {claim}")
    lines.append("\n## Sources Used")
    for source in report.sources_used:
        lines.append(f"- {source}")
    return "\n".join(lines)

async def run_research_agent(state):
    pdf_paths = state["input"]["pdf_paths"]
    pdf_text = extract_text_from_pdfs(pdf_paths)
    state["context"]["documents"].append({
        "type": "pdf_collection",
        "paths": pdf_paths,
        "text": pdf_text
    })
    
    research_chain = researcher_prompt | fast_llm | research_parser
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
