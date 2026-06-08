from pydantic import BaseModel,Field
from typing import Literal
class Asset(BaseModel):
    id:str
    type:Literal["image","video","document","text"]
    path:str
    content:str|None = Field(default=None)