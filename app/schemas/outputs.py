from pydantic import BaseModel
from typing import List
from langchain_core.output_parsers import PydanticOutputParser

class ResearchOutput(BaseModel):
    summary: str
    key_claims: List[str]
    sources_used: List[str]

class WriterOutput(BaseModel):
    title: str
    blog_markdown: str

class Slide(BaseModel):
    slide_number: int
    title: str
    overlay_text: str
    image_prompt: str
    visual_direction: str

class CarouselOutput(BaseModel):
    slides: List[Slide]

class Scene(BaseModel):
    scene_number: int
    visual_description: str
    audio_dialogue: str
    timing: str

class VideoOutput(BaseModel):
    scenes: List[Scene]

# Instantiated Output Parsers
research_parser = PydanticOutputParser(pydantic_object=ResearchOutput)
writer_parser = PydanticOutputParser(pydantic_object=WriterOutput)
carousel_parser = PydanticOutputParser(pydantic_object=CarouselOutput)
video_parser = PydanticOutputParser(pydantic_object=VideoOutput)
