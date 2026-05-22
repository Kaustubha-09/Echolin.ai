# Echolin.ai

> **Spot the Fake. Preserve the Truth.** An AI-powered deepfake detection platform that uses Vision Transformer (ViT) models to classify images and videos as real or fake with confidence scores, paired with an optional LLM layer for explainable analysis.

[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9-blue?logo=typescript)](https://www.typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/ML-PyTorch%20ViT-EE4C2C?logo=pytorch)](https://pytorch.org)
[![Supabase](https://img.shields.io/badge/Auth%20%2B%20DB-Supabase-3ECF8E?logo=supabase)](https://supabase.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Deepfake fraud rose **2,100% since 2019**. Echolin.ai gives anyone — journalists, moderators, students, average users — a way to verify whether an image or video has been manipulated, in seconds, through a clean web interface that requires no AI expertise. **Detection only**: this platform does not generate deepfakes.

---

## Screenshots

| Live Detection | AI Assistant |
|:-:|:-:|
| <img src="Screenshots/01_live_detection.png" width="320" /> | <img src="Screenshots/02_ai_assistant.png" width="320" /> |

| Auth Modal | File Analysis |
|:-:|:-:|
| <img src="Screenshots/03_auth_modal.png" width="320" /> | <img src="Screenshots/04_file_analysis.png" width="320" /> |

---

## Features

- **AI-powered detection** — Vision Transformer (`ashish-001/deepfake-detection-using-ViT`) classifies images as real or fake with a confidence score (92–98% accuracy on standard datasets).
- **Batch upload** — drag-and-drop multiple images at once.
- **Real-time inference** — ~0.5s per image on a standard machine.
- **Conversational AI assistant** — ChatGPT-backed Q&A and explainable breakdowns of detection findings.
- **Detection methods** — facial landmark analysis, edge artifact detection, texture consistency, lighting analysis, frequency-domain analysis.
- **Secure auth** — Supabase Auth with JWT tokens, row-level security on every table.
- **Chat history persistence** — sessions and messages stored per-user.
- **Privacy-first** — uploaded files are stored temporarily; can be configured for auto-deletion.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                              │
│  React 19 + TypeScript + Tailwind                                   │
│  • Upload UI, AuthModal, ChatHistory, SettingsModal, UserProfile    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTP / REST
┌───────────────────────────────▼─────────────────────────────────────┐
│                      Backend API Layer                              │
│  FastAPI (Python) — request handling, auth, routing                 │
└───────────────────────────────┬─────────────────────────────────────┘
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│  Detection Models    │ │   LLM Service        │ │     Supabase         │
│  PyTorch ViT         │ │   ChatGPT (optional) │ │  PostgreSQL + Auth   │
│  (images & videos)   │ │   explainable output │ │  + Storage           │
└──────────────────────┘ └──────────────────────┘ └──────────────────────┘
```

### Project structure

```
Echolin.ai/
├── backend/                    FastAPI service
│   ├── app.py                  Main FastAPI application
│   ├── detector.py             Core detection logic
│   ├── agent.py                LLM agent for explanations
│   ├── llm_service.py          LLM integration
│   └── requirements.txt
│
├── detection_model/            ML model service (FastAPI)
│   ├── fast_api.py
│   ├── deepfake_image.py
│   ├── deepfake_video.py
│   └── requirements.txt
│
├── src/                        React frontend
│   ├── components/             AuthModal, ChatHistory, SettingsModal,
│   │                           UploadComponent, UserProfile
│   ├── services/               openaiService, supabaseService, LLMService
│   ├── App.tsx                 Main app
│   └── index.tsx               Entry point
│
├── assets/                     Static images
├── public/                     Public assets
├── Screenshots/                README captures
├── package.json
└── README.md
```

### Detection pipeline

1. **File upload** — image or video via the web UI.
2. **Preprocessing** — images converted to RGB; videos split into up to 10 frames; files stored temporarily in Supabase Storage.
3. **Model inference** — ViT processes each frame, outputs Real/Fake softmax probabilities.
4. **Post-processing** — per-frame results aggregated for videos; confidence scores normalized.
5. **Optional LLM explanation** — detection result sent to ChatGPT for a plain-English breakdown of indicators.

---

## Tech Stack

### ML & detection
- **Vision Transformer** — `ashish-001/deepfake-detection-using-ViT` from Hugging Face
- **PyTorch** — model inference
- **Transformers (Hugging Face)** — pre-trained ViT loading
- **OpenCV** — video frame extraction

### Backend
- **FastAPI** — Python async web framework
- **CORS** enabled for frontend integration
- **Supabase Python client** — database + storage ops

### Frontend
- **React 19** — UI framework
- **TypeScript** — type-safe components
- **Tailwind CSS** — utility-first styling
- **Supabase JS client** — auth + DB
- **OpenAI SDK** — LLM-based explanations

### Infrastructure
- **Supabase** — Auth, Postgres, Storage
- **OpenAI API** (optional) — ChatGPT for explanations

---

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Supabase account (free tier works)
- OpenAI API key (optional — only for LLM explanations)

### Frontend

```bash
npm install

# Create .env.local
cat > .env.local <<'EOF'
REACT_APP_SUPABASE_URL=your_supabase_project_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
REACT_APP_OPENAI_API_KEY=your_openai_api_key_here   # optional
REACT_APP_BACKEND_URL=http://localhost:8000
EOF

npm start                       # http://localhost:3000
```

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create .env
cat > .env <<'EOF'
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
JWT_SECRET=your_jwt_secret_key
STORAGE_BUCKET=uploads
EOF

uvicorn app:app --reload --port 8000
```

### Detection model service

```bash
cd detection_model
pip install -r requirements.txt
# Models auto-download from Hugging Face on first use
```

### Supabase setup

Run the schema in your Supabase SQL Editor:

```sql
CREATE TABLE chat_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('user', 'agent')),
  content TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

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

ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE detections ENABLE ROW LEVEL SECURITY;

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

Then in Supabase Storage, create a bucket named `uploads` (public or with appropriate policies).

---

## Security & Privacy

- **Supabase Auth** — JWT tokens, email/password sign-in.
- **Row-Level Security** — users can only access their own sessions, messages, and detections.
- **Temporary storage** — files in Supabase Storage can be configured for automatic deletion.
- **No permanent storage by default** — files are not retained after analysis.
- **API keys in env vars** — never committed to source control.
- **Input validation** — file type and size checks reject malicious uploads.
- **CORS** — production deployments restrict cross-origin requests to known domains.

---

## Ethical Use

This platform is for **legitimate deepfake detection only**: media verification, fact-checking, education, content moderation, journalistic verification, personal authenticity checks.

**Prohibited:** creating, distributing, or facilitating deepfakes; harassment, defamation, or non-consensual content; legal or regulatory violations.

**Limitations:** detection accuracy varies by manipulation type; results should be used as one signal among multiple verification methods; false positives and false negatives are possible; this is not a substitute for professional forensic analysis.

---

## Roadmap

### Short-term (0–3 months)
- Frame-by-frame video deepfake detection
- Explainable AI: highlight manipulated regions in fake images
- Browser extension (Twitter, Instagram, news sites)
- Mobile app integration

### Long-term (3–12 months)
- Open API for researchers, journalists, moderators
- Verified content watermarking
- Detection dashboard with trends and risk scores
- Real-time video stream analysis
- Model quantization for inference acceleration
- Multi-language i18n
- CI/CD pipeline

---

## Troubleshooting

| Issue | Fix |
|---|---|
| "Analysis Unavailable" | Check `REACT_APP_OPENAI_API_KEY` in `.env.local`; restart dev server |
| Auth not working | Verify Supabase URL + key; confirm schema is applied; check RLS policies |
| Chat history not saving | Confirm signed-in state; verify Supabase connection; check browser console |

---

## License

[MIT](LICENSE)

---

*Built with a focus on responsible AI and security best practices.*
