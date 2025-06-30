# src/main.py
import uvicorn
from fastapi import FastAPI
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.app.config.settings import UPLOAD_DIR, OUTPUT_DIR, PROCESSED_IMAGES_DIR
from src.app.routes.v1 import router as v1_router

app = FastAPI(title="Foldering by Image Captioning API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)

app.include_router(v1_router)


app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.mount(
    "/processed_images",
    StaticFiles(directory=PROCESSED_IMAGES_DIR),
    name="processed_images",
)


app.mount("/folderisasi", StaticFiles(directory=OUTPUT_DIR), name="folderisasi")

@app.get("/")
def root():
    return {
        "message": "Your API success. Foldering by Image Captioning API is running! 🚀"
    }


def cleanup():
    """Cleanup function untuk shutdown - opsional, bisa dihapus jika ingin persist data"""
    for dir_path in [UPLOAD_DIR, OUTPUT_DIR]:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)
            print(f"Cleaned up {dir_path}")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down application...")
    cleanup()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
