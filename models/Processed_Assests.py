import os
from io import BytesIO
from typing import Optional, List


from pydantic import BaseModel, Field
from pypdf import PdfReader


class ImageAsset(BaseModel):
    asset_id: str
    description: str = ""
    image_bytes: bytes
    ocr_text: Optional[str] = None
    source_document: Optional[str] = None
    page_number: Optional[int] = None


class VideoAsset(BaseModel):
    asset_id: str
    keyframes: List[float] = Field(default_factory=list)
    transcript: Optional[str] = None


class DocumentAsset(BaseModel):
    asset_id: str
    content: str
    page_images: List[ImageAsset] = Field(default_factory=list)


class ProcessedAssets(BaseModel):
    texts: List[str] = Field(default_factory=list)
    document_assets: List[DocumentAsset] = Field(default_factory=list)
    image_assets: List[ImageAsset] = Field(default_factory=list)
    video_assets: List[VideoAsset] = Field(default_factory=list)