from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import base64
import numpy as np
from io import BytesIO
import cv2
from PIL import Image

import os
import aiofiles
import re
import traceback

from model_loader import ModelLoader
from video_preprocessor import VideoPreprocessor


app = FastAPI(title="LumaVoice API", description="AI-powered sign language recognition")

# === Config ===
STATIC_DATA_PATH = "/home/poras9868/data"  # Update this if needed

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max

# === Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://35.201.249.96:5173",
        "http://35.201.249.96:3000",
        "http://35.201.249.96:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Static Mount ===
if os.path.exists(STATIC_DATA_PATH):
    app.mount("/static", StaticFiles(directory=STATIC_DATA_PATH), name="static")
else:
    print(f"⚠️ Warning: Static path {STATIC_DATA_PATH} not found")

# === Ensure upload directory exists ===
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Load model and preprocessor ===
model_loader = ModelLoader()
video_preprocessor = VideoPreprocessor()

# === Helper ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# === Routes ===

@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'message': 'LumaVoice API is running'}

from fastapi import Form

@app.post('/predict')
async def predict_video(
    video: UploadFile = File(None),  # Optional video upload
    test_path: str = Form(None)      # Optional path from frontend test select
):
    try:
        if not video and not test_path:
            raise HTTPException(status_code=400, detail='No video or test_path provided')

        if video:
            # Handle uploaded video
            filename = re.sub(r'[^a-zA-Z0-9._-]', '_', video.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, filename)

            print(f"[DEBUG] Saving uploaded file to: {temp_path}")
            async with aiofiles.open(temp_path, 'wb') as buffer:
                content = await video.read()
                await buffer.write(content)

        # elif test_path:
        #     # Use static test video
        #     temp_path = test_path
        #     print(f"[DEBUG] Using test video path: {temp_path}")
        elif test_path:
            # Convert relative test_path to absolute path
            safe_relative_path = os.path.normpath(test_path).lstrip(os.sep)
            temp_path = os.path.join(STATIC_DATA_PATH, safe_relative_path.split("data/", 1)[-1])
            print(f"[DEBUG] Using test video absolute path: {temp_path}")

        # Preprocess video
        processed_frames = video_preprocessor.process_video(temp_path)
        print(f"[DEBUG] Processed {len(processed_frames)} frames")

        # Predict
        prediction = model_loader.predict(processed_frames)
        print(f"[DEBUG] Prediction raw output: {prediction}")

        # Cleanup uploaded file
        if video and os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            'success': True,
            'prediction': prediction.get('text', '') if isinstance(prediction, dict) else str(prediction),
            'confidence': prediction.get('confidence', 0) if isinstance(prediction, dict) else 0,
            'detected_text': prediction.get('text', '') if isinstance(prediction, dict) else str(prediction),
            'processing_info': {
                'frames_processed': len(processed_frames),
                'video_duration': prediction.get('duration', 0) if isinstance(prediction, dict) else 0
            }
        }

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")



@app.get('/test-videos')
async def get_test_videos():
    try:
        base_path = '/home/poras9868/data/recordings/data'  # <-- Absolute path

        result = {'folders': [], 'videos': {}}

        if os.path.exists(base_path):
            for folder in sorted(os.listdir(base_path)):
                folder_path = os.path.join(base_path, folder)
                if os.path.isdir(folder_path):
                    result['folders'].append(folder)
                    video_files = []
                    for file in os.listdir(folder_path):
                        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.mpg')):
                            video_files.append(file)
                    result['videos'][folder] = sorted(video_files)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to read test videos: {str(e)}')


@app.get('/model/info')
async def model_info():
    try:
        info = model_loader.get_model_info()
        return {
            'model_loaded': info.get('loaded'),
            'model_type': info.get('type'),
            'input_shape': info.get('input_shape'),
            'classes': info.get('classes', [])  # Default to empty list if missing
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to get model info: {str(e)}')


class DetectRequest(BaseModel):
    image: str
    video_path: Optional[str] = None

@app.post("/api/detect-face")
async def detect_face(data: DetectRequest):
    try:
        # Decode base64 image
        image_data = data.image.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        preds = fa.get_landmarks(frame)

        if preds and len(preds) > 0:
            landmarks = preds[0]
            landmark_points = []

            for i, point in enumerate(landmarks):
                if i < 17:
                    landmark_points.append({
                        'x': float(point[0]),
                        'y': float(point[1]),
                        'type': 'face',
                        'confidence': 0.9
                    })
                elif 48 <= i <= 67:
                    landmark_points.append({
                        'x': float(point[0]),
                        'y': float(point[1]),
                        'type': 'mouth_outer' if i <= 59 else 'mouth_inner',
                        'confidence': 0.95
                    })
                # Add more types like eyes, nose if needed

            # Calculate crop region using your function
            crop = measurements(frame)  # [y1, y2, x1, x2]

            return {
                'landmarks': landmark_points,
                'crop_region': {
                    'x': crop[2],
                    'y': crop[0],
                    'width': crop[3] - crop[2],
                    'height': crop[1] - crop[0]
                }
            }

        return {'landmarks': [], 'crop_region': None}
    
    except Exception as e:
        return {'error': str(e), 'landmarks': [], 'crop_region': None}


# === Dev entrypoint ===
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
