from langchain_core.prompts import ChatPromptTemplate
from .model import writer_model 
from langchain_core.prompts import ChatPromptTemplate
from models.llm_output import RefinedBLog
import json
import os
from dotenv import load_dotenv
load_dotenv()
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert Content Architect.

Your task is to create a polished, high-quality blog article using the provided research report and source materials.

Rules:
- Every factual claim must be supported by the provided sources.
- Do not invent facts.
- Preserve technical accuracy.
- Improve clarity, structure, readability, and engagement.
- Create a compelling title.
- Generate references from the supplied source assets.
- Only reference assets that actually appear in the provided context.

You MUST return valid JSON only.

Required JSON schema:

{{
  "title": "string",
  "content": "string",
  "references": [
    {{
      "asset_id": "string",
      "content": "supporting excerpt from source"
    }}
  ]
}}

Requirements:
- title must be a concise blog title.
- content must contain the complete blog article.
- references must contain supporting evidence used to create the article.
- asset_id must correspond to an input asset.
- content inside references must contain the supporting excerpt from that asset.
- Return ONLY JSON.
- Do not wrap the response in markdown.
- Do not include explanations before or after the JSON.
"""
    ),
    (
        "user",
        """
        
        
SOURCE ASSETS

Texts:
{texts}

Documents:
{documents}

Image OCR:
{image_ocr}

Video Transcripts:
{video_transcripts}

Research Report:
{research_report}

Write the final blog.
"""
    )
])

def generate_blog(texts, documents, image_ocr,
                  video_transcripts, research_report)->RefinedBLog:
    messages = writer_prompt.format_messages(
        texts=texts,
        documents=documents,
        image_ocr=image_ocr,
        video_transcripts=video_transcripts,
        research_report=research_report,
    )
    response = writer_model.invoke(messages)
    content = response.content[0]["text"].strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        content = content.replace("json", "", 1).strip()
    data = json.loads(content)
    blog = RefinedBLog.model_validate(data)
    return blog