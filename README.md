# Echolin.ai

**Echolin.ai** is an AI-powered deepfake detection platform designed to identify manipulated images and videos using state-of-the-art machine learning models. The platform combines PyTorch-based detection models with an optional LLM layer for explainable analysis, providing users with confidence scores and detailed insights into potential deepfake indicators.

> **Note**: This platform is designed exclusively for **detection** purposes. It does NOT generate deepfakes.

## Features

- **Multi-Modal Detection**: Analyze both images and videos for deepfake indicators
- **PyTorch-Based ML Models**: Utilizes Vision Transformer (ViT) models trained on deepfake detection datasets
- **Explainable AI**: Optional LLM integration provides detailed explanations of detection results
- **Real-Time Analysis**: Fast processing with confidence scores and detection metrics
- **User Authentication**: Secure user management via Supabase with chat history persistence
- **Interactive AI Assistant**: Conversational interface for deepfake education and analysis
- **Production-Ready Architecture**: Scalable FastAPI backend with React frontend
- **Privacy-Focused**: Secure file handling with temporary storage and user data protection

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  React + TypeScript (User Interface & Interactive Components)  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ HTTP/REST API
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                      Backend API Layer                           │
│  FastAPI (Python) - Request handling, authentication, routing    │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│   Detection  │ │   LLM       │ │  Supabase   │
│   Models     │ │   Service   │ │  (Auth/DB)  │
│              │ │             │ │             │
│ PyTorch ViT  │ │ ChatGPT API │ │ PostgreSQL  │
│ (Images)    │ │ (Optional)   │ │ Storage     │
│ PyTorch ViT  │ │             │ │             │
│ (Videos)    │ │             │ │             │
└──────────────┘ └─────────────┘ └─────────────┘
```

## Tech Stack

### Frontend
- **React 19** - Modern UI framework
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Supabase Client** - Authentication and database integration
- **OpenAI SDK** - LLM integration for explainable analysis

### Backend
- **FastAPI** - High-performance Python web framework
- **PyTorch** - Deep learning framework
- **Transformers (Hugging Face)** - Pre-trained Vision Transformer models
- **OpenCV** - Video processing and frame extraction
- **Supabase Python Client** - Database and storage operations

### Infrastructure & Services
- **Supabase** - Authentication, PostgreSQL database, and file storage
- **OpenAI API** (Optional) - ChatGPT integration for analysis explanations

## Project Structure

```
Echolin.ai/
├── backend/                    # FastAPI backend service
│   ├── app.py                  # Main FastAPI application
│   ├── detector.py             # Core detection logic
│   ├── agent.py                # LLM agent for explanations
│   ├── llm_service.py          # LLM integration service
│   └── requirements.txt        # Python dependencies
│
├── detection_model/            # ML model components
│   ├── fast_api.py             # FastAPI service for detection
│   ├── deepfake_image.py       # Image detection model
│   ├── deepfake_video.py       # Video detection model
│   └── requirements.txt        # ML dependencies
│
├── src/                        # React frontend source
│   ├── components/             # React components
│   │   ├── AuthModal.tsx       # Authentication UI
│   │   ├── ChatHistory.tsx     # Chat history sidebar
│   │   ├── SettingsModal.tsx   # User settings
│   │   ├── UploadComponent.tsx # File upload UI
│   │   └── UserProfile.tsx     # User profile component
│   ├── services/               # Service layer
│   │   ├── LLMService.js       # LLM service client
│   │   ├── openaiService.ts    # OpenAI integration
│   │   └── supabaseService.ts  # Supabase integration
│   ├── App.tsx                 # Main application component
│   └── index.tsx               # Application entry point
│
├── public/                     # Static assets
├── package.json                # Node.js dependencies
├── tsconfig.json               # TypeScript configuration
└── README.md                   # This file
```

## Setup Instructions

### Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.8+
- **Supabase Account** (free tier available)
- **OpenAI API Key** (optional, for LLM explanations)

### Frontend Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment variables**:
   Create a `.env.local` file in the project root:
   ```bash
   # Supabase Configuration (Required)
   REACT_APP_SUPABASE_URL=your_supabase_project_url
   REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key

   # OpenAI Configuration (Optional - for LLM explanations)
   REACT_APP_OPENAI_API_KEY=your_openai_api_key_here

   # Backend API URL
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```
   The application will be available at `http://localhost:3000`

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the `backend` directory:
   ```bash
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   JWT_SECRET=your_jwt_secret_key
   STORAGE_BUCKET=uploads
   ```

5. **Start the FastAPI server**:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

### Detection Model Setup

1. **Navigate to detection_model directory**:
   ```bash
   cd detection_model
   ```

2. **Install ML dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Models are automatically downloaded** from Hugging Face on first use:
   - Model: `ashish-001/deepfake-detection-using-ViT`

### Supabase Database Setup

Run the following SQL in your Supabase SQL Editor:
=======
# DeepShield AI - Advanced Deepfake Detection Platform

An intelligent deepfake detection platform powered by ChatGPT Vision API and advanced AI algorithms.

## 🚀 Features

- **AI-Powered Analysis**: Real-time image analysis using ChatGPT-4 Vision
- **Interactive Chat**: Conversational AI assistant for deepfake education
- **User Authentication**: Secure login with chat history storage
- **Multi-Method Detection**: Comprehensive analysis including facial landmarks, edge artifacts, texture consistency, and lighting analysis
- **Real-time Camera**: Live deepfake detection from camera feed
- **Detailed Reports**: In-depth analysis with confidence scores and recommendations

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Configuration
Create a `.env.local` file in the project root with the following variables:

```bash
# OpenAI Configuration (Required for ChatGPT analysis)
REACT_APP_OPENAI_API_KEY=your_openai_api_key_here

# Supabase Configuration (Required for user auth and chat history)
REACT_APP_SUPABASE_URL=your_supabase_project_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key

# Optional: Other API configurations
REACT_APP_GMI_API_KEY=your_gmi_api_key
REACT_APP_GMI_API_URL=https://api.gmi.cloud/v1/chat/completions
REACT_APP_BACKEND_URL=http://localhost:5000/api/agent-detect
```

### 3. Get Your API Keys

#### OpenAI API Key (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Create a new API key
5. Copy the key and add it to your `.env.local` file

#### Supabase Setup (Required for user features)
1. Go to [Supabase](https://supabase.com) and create a new project
2. In your project dashboard, go to **Settings** → **API**
3. Copy your **Project URL** and **anon/public key**
4. Add them to your `.env.local` file

### 4. Database Setup (Supabase)
In your Supabase project's SQL Editor, run the following schema:
>>>>>>> org/main

```sql
-- Chat Sessions Table
CREATE TABLE chat_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Messages Table
CREATE TABLE chat_messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('user', 'agent')),
  content TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Detections Table
CREATE TABLE detections (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  storage_bucket TEXT NOT NULL,
  analysis_result JSONB,
  confidence FLOAT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'completed'
);

-- Enable Row Level Security
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE detections ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only access their own data)
CREATE POLICY "Users can view own sessions" ON chat_sessions
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sessions" ON chat_sessions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own messages" ON chat_messages
  FOR SELECT USING (
    EXISTS (SELECT 1 FROM chat_sessions WHERE id = chat_messages.session_id AND user_id = auth.uid())
  );

CREATE POLICY "Users can insert own messages" ON chat_messages
  FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM chat_sessions WHERE id = chat_messages.session_id AND user_id = auth.uid())
  );

CREATE POLICY "Users can view own detections" ON detections
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own detections" ON detections
  FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### Storage Bucket Setup

1. In Supabase Dashboard, navigate to **Storage**
2. Create a new bucket named `uploads`
3. Set bucket to **Public** (or configure appropriate policies)
4. Configure CORS if needed for your domain

## How It Works

### Detection Pipeline

1. **File Upload**: User uploads an image or video through the web interface
2. **Preprocessing**: 
   - Images are converted to RGB format
   - Videos are split into frames (up to 10 frames analyzed)
   - Files are temporarily stored in Supabase Storage
3. **Model Inference**: 
   - Vision Transformer (ViT) model processes each frame
   - Model outputs classification probabilities (Real/Fake)
   - Confidence scores are calculated using softmax probabilities
4. **Post-Processing**:
   - Results are aggregated for videos (frame-by-frame analysis)
   - Confidence scores are normalized and formatted
5. **Optional LLM Explanation**:
   - Detection results can be sent to ChatGPT for explainable analysis
   - LLM provides detailed breakdown of detection indicators
   - User-friendly explanations of technical findings

### Detection Methods

The platform employs multiple detection techniques:

- **Facial Landmark Analysis**: Geometric consistency of facial features
- **Edge Artifact Detection**: Identification of unnatural blending patterns
- **Texture Consistency**: Analysis of skin texture and surface patterns
- **Lighting Analysis**: Verification of light source consistency and shadows
- **Frequency Domain Analysis**: Detection of artifacts in frequency space

### Model Architecture

The detection models use Vision Transformers (ViT) pre-trained on deepfake detection datasets. The models are fine-tuned to distinguish between authentic and manipulated media by learning discriminative features in facial regions and surrounding context.

## Security & Privacy

- **Authentication**: Secure user authentication via Supabase Auth with JWT tokens
- **Row-Level Security**: Database-level access control ensures users can only access their own data
- **Temporary Storage**: Uploaded files are stored temporarily and can be configured for automatic deletion
- **No Permanent Storage**: By default, files are not permanently stored after analysis
- **API Key Protection**: All API keys are stored in environment variables, never committed to version control
- **HTTPS**: Production deployments should use HTTPS for all communications
- **Input Validation**: File type and size validation prevents malicious uploads
- **CORS Configuration**: Properly configured CORS policies restrict cross-origin requests

## Ethical Use Disclaimer

**Echolin.ai is designed exclusively for legitimate deepfake detection purposes.**

### Intended Use Cases
- Media verification and fact-checking
- Educational purposes and research
- Content moderation and platform safety
- Journalistic verification
- Personal media authentication

### Prohibited Uses
- **This platform does NOT generate deepfakes**
- Do not use this platform to:
  - Create, distribute, or facilitate the creation of deepfakes
  - Harass, defame, or harm individuals
  - Violate privacy rights or create non-consensual content
  - Mislead or deceive others
  - Violate applicable laws or regulations

### Limitations
- Detection accuracy depends on model training data and may vary across different types of manipulations
- Results should be used as one indicator among multiple verification methods
- False positives and false negatives are possible
- The platform is not a substitute for professional forensic analysis

### Responsibility
Users are responsible for ensuring their use of this platform complies with all applicable laws and ethical guidelines. The developers assume no liability for misuse of this software.

## Future Improvements

- **Enhanced Model Accuracy**: Integration of ensemble models and state-of-the-art detection architectures
- **Real-Time Video Streaming**: Support for live video stream analysis
- **Batch Processing**: API endpoints for processing multiple files simultaneously
- **Advanced Metrics**: Detailed detection metrics dashboard with historical trends
- **Model Explainability**: Enhanced visualization of detection indicators and heatmaps
- **Multi-Language Support**: Internationalization for global accessibility
- **Mobile Application**: Native mobile apps for iOS and Android
- **API Rate Limiting**: Production-grade rate limiting and usage quotas
- **Webhook Integration**: Support for webhook notifications on detection events
- **Custom Model Training**: Tools for fine-tuning models on custom datasets
- **Performance Optimization**: Model quantization and inference acceleration
- **Comprehensive Testing**: Expanded test coverage and CI/CD pipeline

## Author

Developed with a focus on responsible AI and security best practices.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Disclaimer**: This software is provided "as is" without warranty of any kind. Detection results should be verified through multiple methods and professional analysis when critical decisions depend on them.
=======
-- Enable Row Level Security
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies (add the rest of your provided schema here)
```

### 5. Run the Application
```bash
npm start
```

The application will open at `http://localhost:3000`

## 🔍 How It Works

### ChatGPT Vision Analysis
- Upload an image to get real-time analysis from ChatGPT-4 Vision
- Receives detailed assessment of potential deepfake indicators
- Analyzes facial landmarks, edge artifacts, texture consistency, and lighting
- Provides confidence scores and detailed explanations

### Features Available:
- ✅ **Guest Mode**: Use the app without login (limited features)
- ✅ **User Authentication**: Sign up/login to save chat history
- ✅ **Image Analysis**: Upload images for ChatGPT-powered deepfake detection
- ✅ **Interactive Chat**: Ask questions about deepfakes and get expert responses
- ✅ **Chat History**: Logged-in users can view and manage conversation history
- ✅ **Settings**: Customize notifications and privacy preferences

## 🔧 Troubleshooting

### Common Issues:

1. **"Analysis Unavailable" Message**
   - Check if your OpenAI API key is correctly set in `.env.local`
   - Ensure you have sufficient API credits in your OpenAI account
   - Restart the development server after adding environment variables

2. **Authentication Not Working**
   - Verify your Supabase URL and API key are correct
   - Check that you've run the database schema in your Supabase project
   - Ensure RLS policies are properly configured

3. **Chat History Not Saving**
   - Make sure you're logged in
   - Verify Supabase database connection
   - Check browser console for any error messages

## 📱 Usage Tips

- **Best Results**: Use clear, high-resolution images for analysis
- **Privacy**: Your images are processed securely and not stored permanently
- **Accuracy**: ChatGPT Vision provides detailed analysis, but always verify with multiple sources for critical use cases
- **Features**: Sign up for an account to unlock chat history and personalized features

## 🛡️ Security & Privacy

- Images are processed in real-time and not permanently stored
- User authentication is handled securely through Supabase
- Chat history is encrypted and only accessible to the authenticated user
- API keys are stored securely in environment variables

---

**Note**: This application requires an active OpenAI API key to function properly. The free tier includes limited requests per month.
>>>>>>> org/main
