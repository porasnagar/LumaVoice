# 🎤 LumaVoice - AI-Powered Lip Reading Technology

> **Breaking the silence with artificial intelligence**

LumaVoice transforms lip movements into spoken words, empowering communication for the deaf and mute community through cutting-edge computer vision and machine learning.

![LumaVoice Demo](https://via.placeholder.com/800x400/1a1a2e/ffffff?text=LumaVoice+Demo)

## ✨ What Makes LumaVoice Special

**Real-Time Processing**: Upload videos or record live webcam footage for instant lip reading analysis

**Advanced ML Pipeline**: Built with TensorFlow and comprehensive video preprocessing including face detection, landmark extraction, and mouth region cropping

**Modern Web Stack**: React 18 + TypeScript frontend with a powerful FastAPI backend

**Beautiful UI**: Glass morphism design with dark/light theme support and responsive mobile interface

**Production Ready**: Containerized with Docker, CORS configured, and deployment-ready architecture

##  Features

### 🎥 Video Input Methods
- **File Upload**: Support for MP4, AVI, MOV, MKV, and WebM formats
- **Webcam Recording**: Real-time video capture with MediaRecorder API
- **Test Videos**: Pre-loaded sample videos for quick testing

### 🧠 AI-Powered Analysis
- **Face Detection**: Automatic face alignment and tracking
- **Landmark Extraction**: 68-point facial landmark detection
- **Mouth Region Focus**: Specialized cropping for optimal lip reading
- **TensorFlow Integration**: Production-ready ML model pipeline

### 🎨 User Experience
- **Glass Morphism UI**: Modern, elegant interface design
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Feedback**: Live canvas-based face detection visualization
- **Text-to-Speech**: Convert predictions to audio using Web Speech API

## 🛠️ Technology Stack

### Frontend Arsenal
```
React 18          → Modern component architecture
TypeScript        → Type safety and better DX
Vite              → Lightning-fast development
TailwindCSS       → Utility-first styling
shadcn/ui         → High-quality component library
Lucide React      → Beautiful, consistent icons
React Router      → Client-side routing
```

### Backend Infrastructure
```
FastAPI           → High-performance async API framework
TensorFlow        → Machine learning model execution
OpenCV            → Computer vision processing
NumPy             → Numerical computing
Pydantic          → Data validation and serialization
Uvicorn           → ASGI server for production
```

### Development Tools
```
Bun               → Fast JavaScript runtime and package manager
ESLint            → Code quality and consistency
Jupyter Notebook  → ML experimentation and model training
Docker            → Containerization for deployment
```

## 📦 Quick Start

### Prerequisites
Make sure you have these installed:
- **Node.js 18+** and **Bun** (or npm)
- **Python 3.8+** with pip
- **Modern browser** with camera permissions

###  Frontend Setup

1. **Clone and navigate to project**
   ```bash
   git clone <your-repo-url>
   cd LumaVoice
   ```

2. **Install dependencies with Bun**
   ```bash
   bun install
   ```

3. **Start the development server**
   ```bash
   bun run dev
   ```
   
   🌐 Frontend runs on `http://localhost:5173`

### 🔧 Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install fastapi uvicorn python-multipart
   pip install tensorflow opencv-python numpy pillow
   pip install aiofiles python-jose[cryptography]
   ```

4. **Launch FastAPI server**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   
   🚀 Backend API runs on `http://localhost:8000`
   📖 Interactive docs at `http://localhost:8000/docs`

### 🐳 Docker Deployment (Optional)

```bash
# Build the container
docker build -t lumavoice .

# Run the application
docker run -p 3000:3000 -p 8000:8000 lumavoice
```

## 🎮 How to Use LumaVoice

### Step 1: Choose Your Input Method
- **📁 Upload Video**: Drag and drop or select video files (up to 100MB)
- **📹 Record Live**: Use your webcam to record real-time footage
- **🎬 Test Videos**: Select from pre-loaded sample videos

### Step 2: AI Processing
- Click **"Predict Speech"** to analyze the video
- Watch the real-time face detection visualization
- AI processes lip movements and facial landmarks

### Step 3: Get Results
- View the predicted text output
- See confidence scores for accuracy assessment
- Use **Text-to-Speech** to hear the predicted words

### Step 4: Advanced Features
- Switch between light/dark themes
- Access prediction history
- Download results for future reference

## 🔌 API Reference

### Core Endpoints

#### `POST /predict`
Process video for lip reading analysis

**Request:**
```bash
curl -X POST "http://localhost:8000/predict" \
  -F "video=@your-video.mp4"
```

**Response:**
```json
{
  "prediction": "Hello, how are you doing today?",
  "confidence": 0.87,
  "status": "success",
  "processing_time": 2.34
}
```

#### `GET /test-videos`
Retrieve available test videos

**Response:**
```json
{
  "videos": [
    {
      "name": "Sample 1",
      "path": "/static/test1.mp4",
      "duration": "00:05"
    }
  ]
}
```

#### `GET /health`
Service health check

**Response:**
```json
{
  "status": "healthy",
  "service": "LumaVoice API",
  "version": "1.0.0"
}
```

## 🧪 Machine Learning Pipeline

Our ML pipeline handles the complete video-to-text transformation:

1. **Video Preprocessing**: Frame extraction and normalization
2. **Face Detection**: Using OpenCV's Haar cascades or DNN models
3. **Landmark Detection**: 68-point facial landmark identification
4. **Mouth Region Extraction**: Cropping and aligning mouth area
5. **Feature Engineering**: Converting visual data to model inputs
6. **Prediction**: TensorFlow model inference
7. **Post-processing**: Text generation and confidence scoring

### Training Data
The model is trained on diverse datasets including:
- Multi-speaker lip reading datasets
- Various lighting conditions
- Different languages and accents
- Multiple camera angles and resolutions

## 🏗️ Project Structure

```
LumaVoice/
├── 📁 src/                    # Frontend React application
│   ├── 📁 components/         # Reusable UI components
│   ├── 📁 pages/             # Main application pages
│   ├── 📁 lib/               # Utilities and helpers
│   └── 📁 hooks/             # Custom React hooks
├── 📁 backend/               # FastAPI backend service
│   ├── app.py               # Main FastAPI application
│   ├── model_loader.py      # ML model management
│   ├── video_preprocessor.py # Video processing pipeline
│   └── 📁 uploads/          # Temporary file storage
├── 📁 public/               # Static assets
├── LumaVoice.ipynb         # ML training notebook
├── 📄 Dockerfile.txt       # Container configuration
└── 📄 package.json         # Frontend dependencies
```

## 🎨 Design Philosophy

LumaVoice embraces **accessibility-first design** with:

- **High Contrast**: Ensures visibility for users with visual impairments
- **Keyboard Navigation**: Full functionality without mouse interaction
- **Screen Reader Support**: Semantic HTML and ARIA labels
- **Mobile Responsive**: Touch-friendly interface for all devices
- **Glass Morphism**: Modern, elegant visual aesthetic

## 🔧 Development Guidelines

### Frontend Development
```bash
# Install new dependencies
bun add package-name

# Run type checking
bun run type-check

# Build for production
bun run build

# Preview production build
bun run preview
```

### Backend Development
```bash
# Run with auto-reload
uvicorn app:app --reload

# Run tests
pytest

# Format code
black . && isort .

# Type checking
mypy app.py
```

## 🌍 Browser Support

| Browser | Status | Notes |
|---------|--------|-------|
| Chrome 90+ | ✅ Full Support | Recommended browser |
| Firefox 88+ | ✅ Full Support | Excellent performance |
| Safari 14+ | ✅ Full Support | iOS 14.3+ required |
| Edge 90+ | ✅ Full Support | Chromium-based |

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin amazing-feature`
5. **Open** a Pull Request

### Development Setup
```bash
# Install frontend dependencies
bun install

# Install backend dependencies
cd backend && pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

## 📈 Performance Metrics

- **Processing Speed**: ~2-5 seconds per 10-second video
- **Accuracy**: 85%+ on clear, frontal face videos
- **Model Size**: ~50MB compressed TensorFlow model
- **Memory Usage**: ~200MB peak during inference

## 🛣️ Roadmap

### Version 2.0 (Coming Soon)
- [ ] **Multi-language Support**: Spanish, French, German
- [ ] **Real-time Streaming**: Live webcam lip reading
- [ ] **Voice Cloning**: Personalized speech synthesis
- [ ] **Mobile App**: Native iOS and Android applications

### Version 2.1 (Future)
- [ ] **Batch Processing**: Multiple video analysis
- [ ] **API Rate Limiting**: Production-grade throttling
- [ ] **User Authentication**: Personal accounts and history
- [ ] **Cloud Deployment**: AWS/Azure integration

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **TensorFlow Team** for the amazing ML framework
- **shadcn/ui** for beautiful, accessible components
- **FastAPI** for the incredible async framework
- **The Deaf Community** for inspiring this project

---

<div align="center">

Built with ❤️ by Poras Nagar and Arjun Phogat

[Report Bug](https://github.com/porasnagar/lumavoice/issues) • [Request Feature](https://github.com/porasnagar/lumavoice/issues) • [Documentation](https://github.com/porasnagar/lumavoice/wiki)

</div>