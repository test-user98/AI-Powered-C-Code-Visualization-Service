from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"

class FunctionResult(BaseModel):
    name: str
    mermaid_diagram: str
    analysis: Optional[str] = None

class Job(BaseModel):
    id: str
    code: str
    status: JobStatus = JobStatus.QUEUED
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    total_functions: int = 0
    processed_functions: int = 0
    functions: List[FunctionResult] = []
    error_message: Optional[str] = None

class JobCreateRequest(BaseModel):
    code: str

class JobResponse(BaseModel):
    id: str
    status: str
    created_at: datetime
    total_functions: int = 0
    processed_functions: int = 0

class JobDetailResponse(BaseModel):
    id: str
    code: str
    status: str
    created_at: datetime
    updated_at: datetime
    total_functions: int
    processed_functions: int
    functions: List[FunctionResult] = []
    error_message: Optional[str] = None
