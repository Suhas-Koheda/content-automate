from pydantic import BaseModel
from typing import List,Optional

class StatusResponse(BaseModel):
    task_id:str
    status:str
    current_agent:Optional[str]=None
    progress_percentage:int=0
    artifacts:dict={}