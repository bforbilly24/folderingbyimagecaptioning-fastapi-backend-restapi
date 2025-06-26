from fastapi import UploadFile, File, HTTPException, BackgroundTasks
from src.app.services.ServiceFactory import ServiceFactory
from src.app.models.ImageModel import ImageData, UploadResponse, ProcessingProgress
from src.app.services.ProgressTracker import progress_tracker
import tempfile
import os
import shutil
import asyncio

class ImageFolderController:
    def __init__(self):
        self.service = ServiceFactory.get_image_caption_service()

    async def process_images_background(self, files, task_id: str):
        """Background task for processing images"""
        try:
            zip_path, image_data = self.service.process_images(files, task_id)
            result = UploadResponse(
                message="Images processed successfully",
                zip_path=zip_path,
                processed_count=len(files),
                spreadsheet_data=image_data
            )
            progress_tracker.complete_task(task_id, result)
        except Exception as e:
            progress_tracker.complete_task(task_id, error=str(e))

    async def process_folder_background(self, temp_dir: str, task_id: str):
        """Background task for processing folder"""
        try:
            result_zip_path, processed_count, image_data = self.service.process_folder(temp_dir, task_id)
            
            if processed_count == 0:
                progress_tracker.complete_task(task_id, error="No valid images found in the uploaded folder")
                return

            result = UploadResponse(
                message="Folder processed successfully",
                zip_path=result_zip_path,
                processed_count=processed_count,
                spreadsheet_data=image_data
            )
            progress_tracker.complete_task(task_id, result)
        except Exception as e:
            progress_tracker.complete_task(task_id, error=str(e))

    async def upload_and_process_images(self, files: list[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
        """Upload and process images with optional progress tracking"""
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")

        # If background_tasks is provided, use asynchronous processing with progress tracking
        if background_tasks:
            # Create task
            task_id = progress_tracker.create_task("image_processing")
            
            # Save files to temporary storage (since background task needs access)
            temp_files = []
            for file in files:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
                content = await file.read()
                temp_file.write(content)
                temp_file.close()
                
                # Create a mock file object with the temp path
                class TempFile:
                    def __init__(self, path, filename):
                        self.path = path
                        self.filename = filename
                        
                    @property
                    def file(self):
                        return open(self.path, 'rb')
                
                temp_files.append(TempFile(temp_file.name, file.filename))

            # Start background processing
            background_tasks.add_task(self.process_images_background, temp_files, task_id)
            return {"task_id": task_id, "message": "Processing started"}
        
        # Otherwise, use synchronous processing
        else:
            zip_path, image_data = self.service.process_images(files)
            return UploadResponse(
                message="Images processed successfully", 
                zip_path=zip_path,
                processed_count=len(files),
                spreadsheet_data=image_data
            )

    async def upload_and_process_folder(self, files: list[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
        """Upload and process folder with optional progress tracking"""
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")

        # If background_tasks is provided, use asynchronous processing with progress tracking
        if background_tasks:
            # Create task
            task_id = progress_tracker.create_task("folder_processing")

            # Create temporary directory and save files
            temp_dir = tempfile.mkdtemp()
            for file in files:
                file_path = os.path.join(temp_dir, file.filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)

            # Start background processing
            background_tasks.add_task(self.process_folder_background, temp_dir, task_id)
            return {"task_id": task_id, "message": "Processing started"}
        
        # Otherwise, use synchronous processing
        else:
            # Create temporary directory to save uploaded files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save all uploaded files to temp directory
                for file in files:
                    file_path = os.path.join(temp_dir, file.filename)
                    # Create subdirectories if file path contains them
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)

                # Process the folder
                result_zip_path, processed_count, image_data = self.service.process_folder(temp_dir)
                
                if processed_count == 0:
                    raise HTTPException(status_code=400, detail="No valid images found in the uploaded folder")

                return UploadResponse(
                    message="Folder processed successfully",
                    zip_path=result_zip_path,
                    processed_count=processed_count,
                    spreadsheet_data=image_data
                )

    def get_task_progress(self, task_id: str) -> ProcessingProgress:
        """Get current progress for a task"""
        progress = progress_tracker.get_progress(task_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Task not found")
        return progress
