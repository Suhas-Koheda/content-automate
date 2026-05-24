from langchain_core.prompts import ChatPromptTemplate
multimedia_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a Multimedia Director. Create a video script and storyboard sequence. For each scene, specify: Visual scene description, Audio/voiceover dialogue, and timing.\n\n{format_instructions}"),
    ("user", "Create a video storyboard from this source:\n{research_data}")
])
