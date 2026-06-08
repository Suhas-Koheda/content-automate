from langchain_core.prompts import ChatPromptTemplate
researcher_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert Research Analyst. Your job is to extract facts, verify details, and create a structured summary from the provided source context.\n\n{format_instructions}"),
    ("user", "Summarize and fact-check the following information:\nSource: {source_text}\nPDF Context: {pdf_context}")
])