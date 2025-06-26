# Image Foldering by AI Captioning - FastAPI Backend

A powerful FastAPI backend service that automatically categorizes and organizes images into folders based on AI-generated captions. This service supports both individual image uploads and folder uploads with real-time progress tracking.

## 🚀 Features

- **AI-Powered Image Captioning**: Uses ResNet50 + LSTM model for generating accurate image descriptions
- **Automatic Categorization**: Groups images into categories like "people", "activities", "objects", etc.
- **Multiple Upload Methods**: Support for both individual images and folder uploads
- **Real-time Progress Tracking**: WebSocket-like progress updates for frontend integration
- **ZIP Export**: Download organized images with Excel spreadsheet summary
- **Modern API**: RESTful API with OpenAPI/Swagger documentation
- **CORS Support**: Ready for frontend integration

## 📋 Prerequisites

- Python 3.11 or higher
- TensorFlow 2.15.0
- FastAPI
- OpenCV, Pillow for image processing

## 🛠️ Installation

### Method 1: Using UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/bforbilly24/folderingbyimagecaptioning-fastapi-backend-restapi.git
cd folderingbyimagecaptioning-fastapi-backend-restapi

# Install uv if you haven't already
pip install uv

# Install dependencies
uv sync
```

### Method 2: Using Virtual Environment

```bash
# Clone the repository
git clone https://github.com/bforbilly24/folderingbyimagecaptioning-fastapi-backend-restapi.git
cd folderingbyimagecaptioning-fastapi-backend-restapi

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method 3: Using Docker

```bash
# Build the Docker image
docker build -t image-foldering-api .

# Run the container
docker run -p 8000:8000 image-foldering-api
```

## 🚀 Running the Application

### Development Mode

```bash
# Recommended - with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Alternative
python src/main.py
```

### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 📚 API Documentation

### Core Endpoints

#### 1. Upload Multiple Images
```http
POST /v1/upload-images
Content-Type: multipart/form-data
```

Upload multiple images for processing and categorization.

**Parameters:**
- `files`: Multiple image files (JPG, PNG, JPEG)

**Response (Synchronous):**
```json
{
  "message": "Images processed successfully",
  "zip_path": "path/to/hasil_folderisasi.zip",
  "processed_count": 5,
  "spreadsheet_data": [
    {
      "filename": "image1.jpg",
      "caption": "person riding bicycle",
      "category": "kegiatan",
      "cosine_similarity": 0.8765,
      "bleu_score": 0.4321
    }
  ]
}
```

**Response (Asynchronous with Progress Tracking):**
```json
{
  "task_id": "uuid-string",
  "message": "Processing started"
}
```

#### 2. Upload Folder
```http
POST /v1/upload-folder
Content-Type: multipart/form-data
```

Upload an entire folder of images for processing.

#### 3. Check Progress
```http
GET /v1/progress/{task_id}
```

Get real-time progress of background processing tasks.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "current_step": "Generating captions",
  "progress_percentage": 45.5,
  "processed_images": 15,
  "total_images": 33,
  "result": null
}
```

#### 4. Download Results
```http
GET /v1/download/{zip_filename}
```

Download the ZIP file containing categorized images and Excel summary.

For complete API documentation, visit: http://localhost:8000/docs

## 🏗️ Project Structure

```
├── src/
│   ├── main.py                 # FastAPI application entry point
│   └── app/
│       ├── __init__.py
│       ├── config/
│       │   └── settings.py     # Configuration settings
│       ├── controllers/
│       │   └── api/
│       │       └── ImageFolderController.py
│       ├── models/
│       │   └── ImageModel.py   # Pydantic models
│       ├── routes/
│       │   └── v1.py          # API routes
│       ├── services/
│       │   ├── ImageCaptionService.py
│       │   ├── ProgressTracker.py
│       │   └── ServiceFactory.py
│       └── ml_models/
│           ├── v2_image_captioning_resnet50_lstm.h5
│           └── v2_tokenizer.pkl
├── assets/                     # Sample images for testing
├── API_DOCUMENTATION.md        # Detailed API documentation
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🎯 Usage Examples

### Frontend Integration (JavaScript)

#### Synchronous Upload
```javascript
const formData = new FormData();
files.forEach(file => formData.append('files', file));

const response = await fetch('http://localhost:8000/v1/upload-images', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log('Processing complete:', result);
```

#### Asynchronous Upload with Progress Tracking
```javascript
// Start upload
const uploadResponse = await fetch('http://localhost:8000/v1/upload-images', {
    method: 'POST',
    body: formData
});

const { task_id } = await uploadResponse.json();

// Poll for progress
const checkProgress = async () => {
    const progressResponse = await fetch(`http://localhost:8000/v1/progress/${task_id}`);
    const progress = await progressResponse.json();
    
    if (progress.status === 'completed') {
        console.log('Processing complete:', progress.result);
        return;
    }
    
    console.log(`Progress: ${progress.progress_percentage}% - ${progress.current_step}`);
    setTimeout(checkProgress, 1000); // Check every second
};

checkProgress();
```

### cURL Examples

#### Upload Images
```bash
curl -X POST "http://localhost:8000/v1/upload-images" \
     -F "files=@image1.jpg" \
     -F "files=@image2.jpg" \
     -F "files=@image3.jpg"
```

#### Check Progress
```bash
curl -X GET "http://localhost:8000/v1/progress/your-task-id"
```

#### Download Results
```bash
curl -X GET "http://localhost:8000/v1/download/hasil_folderisasi.zip" \
     --output categorized_images.zip
```

## 🔧 Configuration

Key configuration options in `src/app/config/settings.py`:

```python
UPLOAD_DIR = "uploads"           # Directory for uploaded files
OUTPUT_DIR = "folderisasi"       # Directory for processed results
MODEL_PATH = "src/app/ml_models/v2_image_captioning_resnet50_lstm.h5"
TOKENIZER_PATH = "src/app/ml_models/v2_tokenizer.pkl"
```

## 🐳 Docker Deployment

### Dockerfile Example
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./folderisasi:/app/folderisasi
    environment:
      - PYTHONPATH=/app
```

## 🧪 Testing

### Sample Images
Use the images in the `assets/` folder for testing:

```bash
# Test with sample images
curl -X POST "http://localhost:8000/v1/upload-images" \
     -F "files=@assets/tes_1.jpeg" \
     -F "files=@assets/tes_2.jpeg"
```

### API Testing with Swagger UI
Visit http://localhost:8000/docs for interactive API testing.

## 🚨 Troubleshooting

### Common Issues

#### Model Files Missing
```bash
# Ensure model files exist
ls src/app/ml_models/
# Should contain:
# - v2_image_captioning_resnet50_lstm.h5
# - v2_tokenizer.pkl
```

#### Permission Issues
```bash
# On Unix systems, ensure proper permissions
chmod -R 755 uploads/ folderisasi/
```

#### CORS Issues
Update CORS settings in `src/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Memory Issues
For large image batches, consider:
- Reducing batch size
- Increasing system RAM
- Using Docker with memory limits

### Logs and Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Considerations

- **Image Size**: Larger images take more time to process
- **Batch Size**: Processing 10-20 images at once is optimal
- **Memory Usage**: Each image requires ~50MB RAM during processing
- **Storage**: Processed results are stored temporarily and cleaned up on shutdown

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions and support:
- Check the [API Documentation](API_DOCUMENTATION.md)
- Visit the interactive docs at http://localhost:8000/docs
- Open an issue on GitHub

---

**Happy Coding! 🚀**
