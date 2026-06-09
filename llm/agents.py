from langchain.agents import create_agent

tools = []
agent=create_agent(writer_model,tools=tools)
