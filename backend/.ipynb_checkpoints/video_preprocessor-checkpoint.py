import torch
import face_alignment
import cv2
import numpy as np
import tensorflow as tf
from typing import Tuple
import os
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

# Initialize face alignment once
fa = face_alignment.FaceAlignment(
    face_alignment.LandmarksType.TWO_D,
    flip_input=False,
    device='cuda' if torch.cuda.is_available() else 'cpu'
)

class VideoPreprocessor:
    def __init__(self, max_frames=75, target_width=100, target_height=50):
        self.max_frames = max_frames
        self.target_width = target_width
        self.target_height = target_height

    def measurements(self, frame):
        """Extract crop measurements from a single frame with better error handling"""
        try:
            preds = fa.get_landmarks(frame)
            if not preds or len(preds) == 0:
                # Return default crop for mouth region
                h, w = frame.shape[:2]
                return (int(h * 0.4), int(h * 0.8), int(w * 0.2), int(w * 0.8))

            landmarks = preds[0]
            
            # Validate landmarks array
            if landmarks.shape[0] < 68:
                h, w = frame.shape[:2]
                return (int(h * 0.4), int(h * 0.8), int(w * 0.2), int(w * 0.8))
            
            # Key landmarks for mouth region
            nose_base = landmarks[33]
            chin_bottom = landmarks[8]
            lip_center = landmarks[66]
            left_lip = landmarks[48]
            right_lip = landmarks[54]
            left_cheek = landmarks[3]
            right_cheek = landmarks[13]

            # Calculate crop boundaries
            crop_y1 = int(nose_base[1])
            crop_y2 = int((chin_bottom[1] + lip_center[1]) / 2)
            
            # Compute padding based on cheek-to-lip distances
            left_dist = np.linalg.norm(left_lip - left_cheek)
            right_dist = np.linalg.norm(right_lip - right_cheek)
            min_padding = int(min(left_dist, right_dist) * 0.5)  # Reduce padding slightly
            
            crop_x1 = int(left_cheek[0] - min_padding)
            crop_x2 = int(right_cheek[0] + min_padding)

            # Ensure valid crop boundaries
            h, w = frame.shape[:2]
            crop_y1 = max(0, min(crop_y1, h - 10))
            crop_y2 = max(crop_y1 + 10, min(crop_y2, h))
            crop_x1 = max(0, min(crop_x1, w - 10))
            crop_x2 = max(crop_x1 + 10, min(crop_x2, w))
            
            return (crop_y1, crop_y2, crop_x1, crop_x2)
            
        except Exception as e:
            print(f"Error in measurements: {e}")
            h, w = frame.shape[:2]
            return (int(h * 0.4), int(h * 0.8), int(w * 0.2), int(w * 0.8))

    def resize_with_horizontal_padding(self, image):
        """Resize image with proper padding and aspect ratio handling"""
        try:
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=-1)
            
            image = tf.convert_to_tensor(image, dtype=tf.float32)
            current_height = tf.shape(image)[0]
            current_width = tf.shape(image)[1]

            # Always resize to target dimensions
            resized = tf.image.resize(image, [self.target_height, self.target_width])
            
            return resized
            
        except Exception as e:
            print(f"Error in resize_with_horizontal_padding: {e}")
            # Return zero array with correct dimensions
            return tf.zeros([self.target_height, self.target_width, 1], dtype=tf.float32)

    def process_video(self, path: str, debug=False) -> np.ndarray:
        """Process video with enhanced error handling and consistency"""
        if not os.path.exists(path):
            print(f"Error: Video file not found: {path}")
            return self._create_empty_frames()
        
        cap = cv2.VideoCapture(path)
        
        if not cap.isOpened():
            print(f"Error: Could not open video: {path}")
            return self._create_empty_frames()
        
        frames = []
        current_crop = None
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if debug:
            print(f"Processing video: {path}")
            print(f"Total frames in video: {total_frames}")
        
        if total_frames == 0:
            print(f"Warning: No frames found in video: {path}")
            cap.release()
            return self._create_empty_frames()

        while len(frames) < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                if debug:
                    print(f"End of video reached at frame {frame_count}")
                break

            try:
                # Recalibrate crop region every 30 frames or on first frame
                if frame_count % 30 == 0 or current_crop is None:
                    current_crop = self.measurements(frame)

                # Convert to grayscale
                if len(frame.shape) == 3:
                    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                else:
                    frame_gray = frame

                # Apply crop
                y1, y2, x1, x2 = current_crop
                cropped = frame_gray[y1:y2, x1:x2]
                
                # Ensure cropped region is not empty
                if cropped.size == 0:
                    if debug:
                        print(f"Empty crop at frame {frame_count}, using default")
                    h, w = frame_gray.shape
                    cropped = frame_gray[h//4:3*h//4, w//4:3*w//4]

                # Resize with padding
                resized = self.resize_with_horizontal_padding(cropped)
                processed = resized.numpy().squeeze()

                # Ensure correct dimensions
                if processed.shape != (self.target_height, self.target_width):
                    processed = cv2.resize(processed, (self.target_width, self.target_height))

                # Normalize to [0, 1]
                processed = processed.astype(np.float32) / 255.0
                frames.append(processed)
                
                if debug and frame_count < 5:
                    print(f"Frame {frame_count}: shape={processed.shape}, min={processed.min():.3f}, max={processed.max():.3f}")
                
                frame_count += 1
                
            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")
                # Add a zero frame to continue processing
                frames.append(np.zeros((self.target_height, self.target_width), dtype=np.float32))
                frame_count += 1

        cap.release()

        # Pad with last frame or zeros if needed
        while len(frames) < self.max_frames:
            if len(frames) > 0:
                frames.append(frames[-1].copy())
            else:
                frames.append(np.zeros((self.target_height, self.target_width), dtype=np.float32))

        if debug:
            print(f"Final frames count: {len(frames)}")

        # Stack and add batch/channel dimensions
        try:
            frames_array = np.stack(frames)  # (75, 50, 100)
            frames_array = np.expand_dims(frames_array, axis=0)  # (1, 75, 50, 100)
            frames_array = np.expand_dims(frames_array, axis=-1)  # (1, 75, 50, 100, 1)
            
            if debug:
                print(f"Final array shape: {frames_array.shape}")
                print(f"Data range: [{frames_array.min():.3f}, {frames_array.max():.3f}]")
            
            return frames_array
            
        except Exception as e:
            print(f"Error stacking frames: {e}")
            return self._create_empty_frames()

    def _create_empty_frames(self):
        """Create empty frame array with correct dimensions"""
        empty = np.zeros((self.target_height, self.target_width), dtype=np.float32)
        frames = [empty] * self.max_frames
        frames_array = np.stack(frames)
        frames_array = np.expand_dims(frames_array, axis=0)
        frames_array = np.expand_dims(frames_array, axis=-1)
        return frames_array


# Enhanced prediction function
def predict_video(video_path, model=None, label_encoder=None, max_frames=75, debug=False):
    """Predict text from a video file with enhanced preprocessing"""
    
    if model is None or label_encoder is None:
        print("Error: Model and label_encoder must be provided")
        return "Error: Model not loaded"
    
    try:
        # Initialize preprocessor
        preprocessor = VideoPreprocessor(
            max_frames=max_frames, 
            target_width=100, 
            target_height=50
        )
        
        # Process video
        print(f"Processing video: {video_path}")
        frames = preprocessor.process_video(video_path, debug=debug)
        
        if debug:
            print(f"Processed frames shape: {frames.shape}")
            print(f"Frames data range: [{frames.min():.3f}, {frames.max():.3f}]")
        
        # Check if frames are valid
        if np.all(frames == 0):
            return "Error: No valid frames processed"
        
        # Make prediction
        print("Making prediction...")
        y_pred = model.predict(frames, verbose=0)
        
        if debug:
            print(f"Prediction shape: {y_pred.shape}")
            print(f"Prediction sample: {y_pred[0, :5, :5]}")  # Show first 5x5 of prediction
        
        # Decode using CTC
        decoded, _ = tf.keras.backend.ctc_decode(
            y_pred,
            input_length=np.ones(y_pred.shape[0]) * y_pred.shape[1],
            greedy=True
        )
        
        # Convert to words
        sequence = decoded[0].numpy()[0]
        
        if debug:
            print(f"Decoded sequence: {sequence}")
        
        # Filter out invalid indices and convert to words
        valid_indices = sequence[sequence >= 0]
        
        if len(valid_indices) == 0:
            return "No words detected"
        
        try:
            words = []
            for idx in valid_indices:
                if idx < len(label_encoder.classes_):
                    word = label_encoder.inverse_transform([idx])[0]
                    words.append(word)
            
            predicted_text = ' '.join(words) if words else "No words detected"
            
            if debug:
                print(f"Valid indices: {valid_indices}")
                print(f"Converted words: {words}")
            
            print(f"Predicted: {predicted_text}")
            return predicted_text
            
        except Exception as e:
            print(f"Error converting indices to words: {e}")
            return f"Error in word conversion: {str(e)}"
        
    except Exception as e:
        error_msg = f"Error predicting video {video_path}: {str(e)}"
        print(error_msg)
        return error_msg


def load_trained_model(model_path='lipreading_model_predict.h5', label_encoder_path='label_encoder.pkl'):
    """Load trained model and label encoder with better error handling"""
    try:
        if not os.path.exists(model_path):
            print(f"Error: Model file not found: {model_path}")
            return None, None
            
        if not os.path.exists(label_encoder_path):
            print(f"Error: Label encoder file not found: {label_encoder_path}")
            return None, None
        
        model = load_model(model_path)
        with open(label_encoder_path, 'rb') as f:
            label_encoder = pickle.load(f)
        
        print(f"✅ Model loaded from {model_path}")
        print(f"✅ Label encoder loaded with {len(label_encoder.classes_)} classes")
        print(f"✅ Model input shape: {model.input_shape}")
        
        return model, label_encoder
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        return None, None


# Usage example
if __name__ == "__main__":
    # Load model
    model, label_encoder = load_trained_model()
    
    if model is not None and label_encoder is not None:
        # Test on a video file
        video_path = "path/to/your/test/video.mp4"
        result = predict_video(video_path, model, label_encoder, debug=True)
        print(f"Final result: {result}")