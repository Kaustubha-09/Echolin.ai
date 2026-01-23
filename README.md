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
