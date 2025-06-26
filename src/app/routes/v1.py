# src/app/routes/v1.py
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from src.app.controllers.api.ImageFolderController import ImageFolderController
from src.app.config.settings import OUTPUT_DIR
import os

router = APIRouter(prefix="/v1", tags=["Image Folding"])
controller = ImageFolderController()

@router.post("/upload-images")
async def upload_images(files: list[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
    """Upload multiple images for processing and categorization with progress tracking"""
    return await controller.upload_and_process_images(files, background_tasks)

@router.post("/upload-folder")
async def upload_folder(files: list[UploadFile] = File(...), background_tasks: BackgroundTasks = None):
    """Upload folder contents (multiple files) for processing and categorization with progress tracking"""
    return await controller.upload_and_process_folder(files, background_tasks)

@router.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """Get current progress for a processing task"""
    return controller.get_task_progress(task_id)

@router.get("/download")
async def download_zip():
    """Download the ZIP file containing categorized images and Excel report"""
    zip_path = os.path.join(OUTPUT_DIR, "hasil_folderisasi.zip")
    print("ZIP Path:", zip_path)  # Debug
    if os.path.exists(zip_path):
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="hasil_folderisasi.zip"
        )
    return {"error": "ZIP file not found"}