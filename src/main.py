# src/app/main.py
import uvicorn
from fastapi import FastAPI
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware
from src.app.config.settings import UPLOAD_DIR, OUTPUT_DIR
from src.app.routes.v1 import router as v1_router

app = FastAPI(title="Foldering by Image Captioning API")

# Tambahkan CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Izinkan origin Vite dev server
    allow_credentials=True,
    allow_methods=["*"],  # Izinkan semua method (GET, POST, dll.)
    allow_headers=["*"],  # Izinkan semua header
)

app.include_router(v1_router)

def cleanup():
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