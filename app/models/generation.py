from pydantic import BaseModel
from typing import List,Optional
class GenerationRequest(BaseModel):
    source_text:Optional[str]=None
    pdf_paths:Optional[list[str]]=None
    style_sample:Optional[str]=None
    channels:List[str]=[]
    template_path:Optional[str]=None

class GenerationResponse(BaseModel):
    task_id:str
    status:str