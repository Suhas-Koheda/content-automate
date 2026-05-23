from langchain_core.prompts import ChatPromptTemplate

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert Content Architect. Take the user's draft blog, style sample, and the researcher's fact-checked report to write a polished, high-quality, formatted Markdown blog post."),
    ("user", "Draft Blog: {draft_blog}\nStyle Sample: {style_sample}\nResearcher Report: {research_report}")
])
