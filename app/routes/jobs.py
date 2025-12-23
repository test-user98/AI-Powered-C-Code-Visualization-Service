from fastapi import APIRouter, HTTPException
from typing import List
from app.models.job import JobCreateRequest, JobResponse, JobDetailResponse
from app.services.job_service import job_service

router = APIRouter()

@router.post("/jobs", response_model=dict)
async def create_job(request: JobCreateRequest):
    """Create a new analysis job"""
    try:
        job_id = job_service.create_job(request.code)
        return {"job_id": job_id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs():
    """Get all jobs with their status"""
    try:
        jobs = job_service.get_all_jobs()
        return [
            JobResponse(
                id=job.id,
                status=job.status.value,
                created_at=job.created_at,
                total_functions=job.total_functions,
                processed_functions=job.processed_functions
            )
            for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job(job_id: str):
    """Get detailed information about a specific job"""
    try:
        job = job_service.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        response = JobDetailResponse(
            id=job.id,
            code=job.code,
            status=job.status.value,
            created_at=job.created_at,
            updated_at=job.updated_at,
            total_functions=job.total_functions,
            processed_functions=job.processed_functions,
            functions=job.functions,
            error_message=job.error_message
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")
