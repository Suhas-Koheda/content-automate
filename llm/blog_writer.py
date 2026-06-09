from langchain_core.prompts import ChatPromptTemplate
from models import writer_model 
from langchain_core.prompts import ChatPromptTemplate
from ../models.llm_output import RefinedBLog
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

{
  "title": "string",
  "content": "string",
  "references": [
    {
      "asset_id": "string",
      "content": "supporting excerpt from source"
    }
  ]
}

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
    response = writer_model(messages)
    data = json.loads(response.content)
    blog = RefinedBLog.model_validate(data)
    return blog


if __name__ == "__main__":
    from utils.Ingestor import (
        process_image,
        process_video,
        process_pdfs,
        merge_processed_assets,
    )
    from models.Processed_Assests import ProcessedAssets

    # Initialize processed assets container
    all_assets = ProcessedAssets()

    # Process one sample document from ~/Downloads folder
    downloads_path = os.path.expanduser("~/Downloads")
    
    # Find first PDF file in Downloads
    documents_in_downloads = []
    if os.path.exists(downloads_path):
        for file in os.listdir(downloads_path):
            if file.lower().endswith(".pdf"):
                documents_in_downloads.append(
                    os.path.join(downloads_path, file)
                )
                break  # Only take first one

    assets_to_process = {
        "images": [],  # e.g., ["path/to/image.png"]
        "videos": [],  # e.g., ["path/to/video.mp4"]
        "documents": documents_in_downloads,  # One sample PDF from ~/Downloads
    }

    # Process images
    for image_path in assets_to_process["images"]:
        processed = process_image(image_path)
        merge_processed_assets(all_assets, processed)

    # Process videos
    for video_path in assets_to_process["videos"]:
        processed = process_video(video_path)
        merge_processed_assets(all_assets, processed)

    # Process documents
    for doc_path in assets_to_process["documents"]:
        processed = process_pdfs(doc_path)
        merge_processed_assets(all_assets, processed)

    # Generate blog from processed assets
    blog = generate_blog(
        texts="\n".join(all_assets.texts),
        documents="\n".join(
            [doc.content for doc in all_assets.document_assets]
        ),
        image_ocr="\n".join(
            [img.ocr_text or "" for img in all_assets.image_assets]
        ),
        video_transcripts="\n".join(
            [vid.transcript or "" for vid in all_assets.video_assets]
        ),
        research_report="",  # Add research report if available
    )

    print("Generated Blog:")
    print(f"Title: {blog.title}")
    print(f"Content:\n{blog.content}")
    print(f"References: {blog.references}")