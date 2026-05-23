from langchain_core.prompts import ChatPromptTemplate
visual_designer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Visual Strategist. Design a 5-10 slide social media carousel based on the research. Specify slide titles, overlay text, and detailed descriptions for background images."),
    ("user", "Design a carousel from this source:\n{research_data}")
])
