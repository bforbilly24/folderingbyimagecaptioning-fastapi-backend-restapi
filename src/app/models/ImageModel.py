#  src/app/models/ImageModel.py
from pydantic import BaseModel
from typing import List, Optional, Union


class ImageData(BaseModel):
    filename: str
    caption: str
    category: str
    image_path: Optional[str] = None


class ImageCategorization(BaseModel):
    filename: str
    caption: str
    category: str
    cosine_similarity: float
    bleu_score: float
    image_path: Optional[str] = None


class UploadResponse(BaseModel):
    message: str
    zip_path: str
    processed_count: int
    spreadsheet_data: List[ImageCategorization]


class AsyncResponse(BaseModel):
    task_id: str
    message: str


class ProcessingStep(BaseModel):
    step_id: int
    text: str
    status: str
    timestamp: Optional[str] = None


class ProcessingProgress(BaseModel):
    task_id: str
    current_step: int
    total_steps: int
    steps: List[ProcessingStep]
    is_completed: bool
    result: Optional[UploadResponse] = None
    error: Optional[str] = None


APIResponse = Union[UploadResponse, AsyncResponse]
