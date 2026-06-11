from pydantic import BaseModel,Field
from typing import Literal,Optional,List
class Evidence(BaseModel):
    asset_id:str
    content:str
class RefinedBLog(BaseModel):
    title:str
    content:str
    references:List[Evidence]
class ImageScript(BaseModel):
    _id:str
    image_prompt:str
    scene_no:int
    narration:str
class VideoScript(BaseModel):
    _id:str
    text:str
class ImageScenes(BaseModel):
    scenes:List[ImageScript]
class GenerationResult(BaseModel):
    refined_blog:RefinedBLog
    image_script:ImageScenes
    video_script:VideoScript