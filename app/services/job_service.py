import threading
import uuid
from typing import Dict, List
from datetime import datetime
from app.models.job import Job, JobStatus, FunctionResult
import logging
import asyncio

logger = logging.getLogger(__name__)

# Import manager for broadcasting (avoid circular import)
def get_manager():
    try:
        from app.main import manager
        return manager
    except ImportError:
        return None

class JobService:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.lock = threading.Lock()
        self.worker_thread = None
        self.job_queue = []
        self.start_worker()

    def create_job(self, code: str) -> str:
        """Create a new job and return its ID"""
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, code=code)
        
        with self.lock:
            self.jobs[job_id] = job
            self.job_queue.append(job_id)
        
        logger.info(f"Created job {job_id}")
        return job_id

    def get_job(self, job_id: str) -> Job:
        """Get a job by ID"""
        with self.lock:
            return self.jobs.get(job_id)

    def get_all_jobs(self) -> List[Job]:
        """Get all jobs"""
        with self.lock:
            return list(self.jobs.values())

    def update_job(self, job: Job):
        """Update a job in storage"""
        with self.lock:
            job.updated_at = datetime.now()
            self.jobs[job.id] = job

        # Broadcast job update to connected WebSocket clients
        try:
            manager = get_manager()
            if manager:
                # Create update message
                update_message = {
                    "type": "job_update",
                    "job_id": job.id,
                    "status": job.status.value,
                    "total_functions": job.total_functions,
                    "processed_functions": job.processed_functions,
                    "updated_at": job.updated_at.isoformat()
                }
                # Schedule broadcast in event loop
                asyncio.create_task(manager.broadcast(update_message))
        except Exception as e:
            logger.error(f"Failed to broadcast job update: {e}")

    def start_worker(self):
        """Start the background worker thread"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=self._process_jobs, daemon=True)
            self.worker_thread.start()
            logger.info("Started background worker thread")

    def _process_jobs(self):
        """Background worker that processes jobs from the queue"""
        from app.services.code_analyzer import CodeAnalyzer
        
        analyzer = CodeAnalyzer()
        
        while True:
            job_id = None
            with self.lock:
                if self.job_queue:
                    job_id = self.job_queue.pop(0)
            
            if job_id:
                try:
                    job = self.get_job(job_id)
                    if job:
                        logger.info(f"Processing job {job_id}")
                        self._process_job(job, analyzer)
                except Exception as e:
                    logger.error(f"Error processing job {job_id}: {e}")
                    job = self.get_job(job_id)
                    if job:
                        job.status = JobStatus.FAILED
                        job.error_message = str(e)
                        self.update_job(job)

    def _process_job(self, job: Job, analyzer: 'CodeAnalyzer'):
        """Process a single job"""
        try:
            # Update status to in progress
            job.status = JobStatus.IN_PROGRESS
            self.update_job(job)
            
            # Step 1: Find functions using ast-grep
            functions = analyzer.find_functions(job.code)
            job.total_functions = len(functions)
            self.update_job(job)

            logger.info(f"Found {len(functions)} functions in job {job.id}")
            
            # Step 2: Process each function
            for func_name in functions:
                try:
                    # Generate Mermaid diagram using LLM
                    mermaid_diagram = analyzer.generate_mermaid_diagram(job.code, func_name)

                    function_result = FunctionResult(
                        name=func_name,
                        mermaid_diagram=mermaid_diagram
                    )
                    job.functions.append(function_result)
                    logger.info(f"Added function result for {func_name}")

                    job.processed_functions += 1
                    self.update_job(job)
                    
                except Exception as e:
                    logger.error(f"Error processing function {func_name}: {e}")
                    # Still add the function result even if processing failed, with empty diagram
                    function_result = FunctionResult(
                        name=func_name,
                        mermaid_diagram=f"flowchart TD\n    A[{func_name}] --> B[Error: {str(e)[:50]}]"
                    )
                    job.functions.append(function_result)
                    job.processed_functions += 1
                    self.update_job(job)
            
            # Step 3: Mark job as complete
            job.status = JobStatus.SUCCESS
            self.update_job(job)
            logger.info(f"Completed job {job.id} with {len(job.functions)} functions")
            
        except Exception as e:
            logger.error(f"Job {job.id} failed: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            self.update_job(job)

# Global job service instance
job_service = JobService()
