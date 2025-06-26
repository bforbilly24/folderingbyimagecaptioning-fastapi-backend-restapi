import uuid
import asyncio
from datetime import datetime
from typing import Dict, List
from src.app.models.ImageModel import ProcessingProgress, ProcessingStep

class ProgressTracker:
    _instance = None
    _progress_store: Dict[str, ProcessingProgress] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProgressTracker, cls).__new__(cls)
        return cls._instance

    def create_task(self, task_type: str = "image_processing") -> str:
        """Create a new processing task and return task ID"""
        task_id = str(uuid.uuid4())
        
        # Define processing steps based on task type
        if task_type == "image_processing":
            steps = [
                ProcessingStep(step_id=0, text="Initializing image processing...", status="pending"),
                ProcessingStep(step_id=1, text="Loading AI models...", status="pending"),
                ProcessingStep(step_id=2, text="Extracting image features...", status="pending"),
                ProcessingStep(step_id=3, text="Generating captions...", status="pending"),
                ProcessingStep(step_id=4, text="Categorizing images...", status="pending"),
                ProcessingStep(step_id=5, text="Organizing into folders...", status="pending"),
                ProcessingStep(step_id=6, text="Creating Excel report...", status="pending"),
                ProcessingStep(step_id=7, text="Generating ZIP file...", status="pending"),
                ProcessingStep(step_id=8, text="Processing completed!", status="pending")
            ]
        else:  # folder_processing
            steps = [
                ProcessingStep(step_id=0, text="Initializing folder processing...", status="pending"),
                ProcessingStep(step_id=1, text="Loading AI models...", status="pending"),
                ProcessingStep(step_id=2, text="Scanning folder contents...", status="pending"),
                ProcessingStep(step_id=3, text="Extracting image features...", status="pending"),
                ProcessingStep(step_id=4, text="Generating captions...", status="pending"),
                ProcessingStep(step_id=5, text="Categorizing images...", status="pending"),
                ProcessingStep(step_id=6, text="Organizing into folders...", status="pending"),
                ProcessingStep(step_id=7, text="Creating Excel report...", status="pending"),
                ProcessingStep(step_id=8, text="Generating ZIP file...", status="pending"),
                ProcessingStep(step_id=9, text="Processing completed!", status="pending")
            ]

        progress = ProcessingProgress(
            task_id=task_id,
            current_step=0,
            total_steps=len(steps),
            steps=steps,
            is_completed=False
        )
        
        self._progress_store[task_id] = progress
        return task_id

    def update_step(self, task_id: str, step_id: int, status: str = "processing") -> bool:
        """Update the status of a specific step"""
        if task_id not in self._progress_store:
            return False
        
        progress = self._progress_store[task_id]
        
        if step_id < len(progress.steps):
            progress.steps[step_id].status = status
            progress.steps[step_id].timestamp = datetime.now().isoformat()
            
            if status == "processing":
                progress.current_step = step_id
            elif status == "completed":
                progress.current_step = step_id + 1
                
        return True

    def complete_task(self, task_id: str, result=None, error: str = None) -> bool:
        """Mark task as completed with result or error"""
        if task_id not in self._progress_store:
            return False
        
        progress = self._progress_store[task_id]
        progress.is_completed = True
        
        if error:
            progress.error = error
            # Mark current step as error
            if progress.current_step < len(progress.steps):
                progress.steps[progress.current_step].status = "error"
        else:
            progress.result = result
            # Mark all steps as completed
            for step in progress.steps:
                if step.status != "completed":
                    step.status = "completed"
                    step.timestamp = datetime.now().isoformat()
            progress.current_step = len(progress.steps)
            
        return True

    def get_progress(self, task_id: str) -> ProcessingProgress:
        """Get current progress for a task"""
        return self._progress_store.get(task_id)

    def cleanup_task(self, task_id: str) -> bool:
        """Remove task from store (optional cleanup)"""
        if task_id in self._progress_store:
            del self._progress_store[task_id]
            return True
        return False

    def get_all_tasks(self) -> Dict[str, ProcessingProgress]:
        """Get all tasks (for debugging)"""
        return self._progress_store.copy()

# Singleton instance
progress_tracker = ProgressTracker()
