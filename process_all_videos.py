import face_alignment
import cv2
import os
import numpy as np
import subprocess
from pathlib import Path

# Load face alignment model once
fa = face_alignment.FaceAlignment(face_alignment.LandmarksType.TWO_D, device='cpu', flip_input=False)

# Input/output base dirs
input_base = Path("videos/videos")
output_base = Path("crop_videos")

# Ensure output root exists
output_base.mkdir(parents=True, exist_ok=True)

# Function to process a single video
def process_video(input_path: Path, output_path: Path):
    temp_audio = "temp_audio.mp3"
    temp_cropped = "temp_cropped.mp4"

    # Extract audio
    subprocess.run(["ffmpeg", "-y", "-i", str(input_path), "-q:a", "0", "-map", "a", temp_audio], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Open video
    cap = cv2.VideoCapture(str(input_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(temp_cropped, cv2.VideoWriter_fourcc(*'mp4v'), fps, (128, 128))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        preds = fa.get_landmarks(frame)
        if preds:
            landmarks = preds[0]
            lips = landmarks[48:68]
            x, y, w, h = cv2.boundingRect(np.array(lips))
            margin = 10
            x = max(x - margin, 0)
            y = max(y - margin, 0)
            cropped = frame[y:y + h + 2 * margin, x:x + w + 2 * margin]
            if cropped.size == 0:
                continue
            cropped = cv2.resize(cropped, (128, 128))
            out.write(cropped)

    cap.release()
    out.release()

    # Merge with audio
    subprocess.run([
        "ffmpeg", "-y", "-i", temp_cropped, "-i", temp_audio,
        "-c:v", "copy", "-c:a", "aac", "-strict", "experimental",
        str(output_path)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Cleanup temp files
    os.remove(temp_audio)
    os.remove(temp_cropped)
    print(f"✅ Processed: {input_path} → {output_path}")

# Walk through input directories
for speaker_folder in input_base.glob("s*"):
    if not speaker_folder.is_dir():
        continue

    out_speaker_folder = output_base / speaker_folder.name
    out_speaker_folder.mkdir(parents=True, exist_ok=True)

    for video_file in speaker_folder.glob("*.mp4"):
        out_path = out_speaker_folder / video_file.name
        process_video(video_file, out_path)
