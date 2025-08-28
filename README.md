# LumaVoice - AI-Powered Lip Reading

LumaVoice is a full-stack web application that helps mute users by converting lip movement videos into text and then speech. The app uses AI-powered lip reading technology to analyze video input and generate speech output.

## Features

- **Video Upload**: Upload video files for lip reading analysis
- **Webcam Recording**: Record videos directly using your device's camera
- **AI Lip Reading**: Convert lip movements to text using machine learning
- **Text-to-Speech**: Convert predicted text to spoken audio
- **Modern UI**: Clean, responsive interface built with React and TailwindCSS
- **Real-time Processing**: Fast video analysis with immediate results

## Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **shadcn/ui** component library
- **Lucide React** for icons
- **React Router** for navigation

### Backend
- **Flask** (Python) - runs locally
- **REST API** for video processing
- **Machine Learning** integration ready

## Setup Instructions

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Modern web browser with camera access

### Frontend Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd lumavoice
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:8080`

### Backend Setup (Flask)

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask flask-cors
   ```

3. **Create the Flask backend** - Save as `app.py`:
   ```python
   from flask import Flask, request, jsonify
   from flask_cors import CORS
   import os
   import tempfile
   
   app = Flask(__name__)
   CORS(app)  # Enable CORS for all routes
   
   @app.route('/predict', methods=['POST'])
   def predict():
       try:
           # Check if video file is present
           if 'video' not in request.files:
               return jsonify({'error': 'No video file provided'}), 400
           
           video_file = request.files['video']
           
           if video_file.filename == '':
               return jsonify({'error': 'No video file selected'}), 400
           
           # Save the uploaded file temporarily
           with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
               video_file.save(temp_file.name)
               temp_filename = temp_file.name
           
           # TODO: Add your actual lip reading model here
           # For now, return dummy predictions
           dummy_predictions = [
               "Hello, how are you?",
               "Thank you very much",
               "Good morning everyone",
               "I hope you have a great day",
               "Please help me with this",
               "Nice to meet you",
               "Have a wonderful time",
               "See you later",
               "Take care of yourself",
               "What are you doing?"
           ]
           
           import random
           prediction = random.choice(dummy_predictions)
           
           # Clean up temporary file
           os.unlink(temp_filename)
           
           return jsonify({
               'prediction': prediction,
               'confidence': 0.85,
               'status': 'success'
           })
           
       except Exception as e:
           return jsonify({'error': str(e)}), 500
   
   @app.route('/health', methods=['GET'])
   def health():
       return jsonify({'status': 'healthy', 'service': 'LumaVoice API'})
   
   if __name__ == '__main__':
       app.run(debug=True, host='0.0.0.0', port=5000)
   ```

4. **Start the Flask server**
   ```bash
   python app.py
   ```

   The backend will be available at `http://localhost:5000`

## Usage

1. **Open the application** in your browser at `http://localhost:8080`

2. **Choose input method**:
   - **Upload Video**: Click "Upload Video" tab and drag/drop or select a video file
   - **Record Video**: Click "Record Video" tab, allow camera access, and record yourself speaking

3. **Analyze the video**: Click the "Predict Speech" button to send the video to the backend

4. **View results**: The predicted text will appear in the results section

5. **Convert to speech**: Click the "Speak" button to hear the predicted text using text-to-speech

## API Endpoints

### POST /predict
Analyzes a video file for lip reading and returns predicted text.

**Request**:
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `video` file

**Response**:
```json
{
  "prediction": "Hello, how are you?",
  "confidence": 0.85,
  "status": "success"
}
```

### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "LumaVoice API"
}
```

## Development

### Frontend Development
- The app uses TypeScript for type safety
- Components are built with shadcn/ui and styled with TailwindCSS
- Video handling uses modern browser APIs (MediaRecorder, getUserMedia)
- Text-to-speech uses the Web Speech API

### Backend Development
- Flask serves as the API backend
- CORS is enabled for cross-origin requests
- File uploads are handled securely with temporary files
- Ready for integration with machine learning models

## Browser Compatibility

- **Chrome/Edge**: Full support
- **Firefox**: Full support  
- **Safari**: Full support (iOS 14.3+)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Future Enhancements

- Real machine learning model integration
- Multiple language support
- Voice customization options
- Video preprocessing features
- Batch processing capabilities
- User authentication and history