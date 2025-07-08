# 🩺 Diabetes Health Assistant

A multilingual, AI-powered diabetes management companion that provides personalized health support in 14 Indian languages.

## 🌟 Features

### 🗣️ Multilingual Support
- **14 Indian Languages**: English, Hindi, Gujarati, Bengali, Tamil, Telugu, Kannada, Malayalam, Punjabi, Marathi, Urdu, Assamese, Odia, Sanskrit
- **Dynamic Language Detection**: Automatically detects input language
- **Real-time Translation**: Seamless translation between languages
- **Localized Interface**: Complete UI translation in selected language

### 🤖 AI-Powered Intelligence
- **SUTRA-V2 Integration**: Advanced multilingual AI model
- **Google Gemini**: Powerful language processing
- **Mem0 Memory**: Persistent user context and history
- **Personalized Responses**: Context-aware medical advice

### 👤 User Management
- **User Registration**: Step-by-step onboarding process
- **Profile Management**: Store diabetes type, medications, symptoms
- **Memory Persistence**: Remember user preferences and history
- **Session Management**: Secure user sessions

### 💬 Chat Interface
- **Real-time Chat**: Interactive conversation interface
- **Medical Context**: Diabetes-specific health advice
- **India-specific Guidance**: Localized medical recommendations
- **Chat History**: Persistent conversation memory

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Streamlit
- Required API keys (see setup below)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/diabetes-health-assistant.git
cd diabetes-health-assistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Get API Keys**
   - **SUTRA API**: Get your key from [Two AI Sutra](https://www.two.ai/sutra/api)
   - **MEM0 API**: Get your key from [Mem0 Dashboard](https://app.mem0.ai/dashboard/)

4. **Run the application**
```bash
streamlit run app.py
```

5. **Access the app**
   - Open your browser and go to `http://localhost:8501`
   - Enter your API keys in the sidebar
   - Select your preferred language
   - Start chatting!

## 📋 Requirements

Create a `requirements.txt` file with:

```txt
streamlit>=1.28.0
agno>=0.1.0
google-generativeai>=0.3.0
mem0ai>=0.1.0
```

## 🛠️ Setup Guide

### 1. API Configuration

#### SUTRA API Key
1. Visit [Two AI Sutra](https://www.two.ai/sutra/api)
2. Create an account or log in
3. Generate your API key
4. Enter it in the sidebar when running the app

#### MEM0 API Key
1. Go to [Mem0 Dashboard](https://app.mem0.ai/dashboard/)
2. Sign up or log in
3. Create a new API key
4. Enter it in the sidebar when running the app

### 2. User Registration

First-time users need to complete a 7-step registration:

1. **Full Name**: Your complete name
2. **Age**: Your current age
3. **Gender**: Male, Female, or Other
4. **Diabetes Type**: Type 1, Type 2, or Gestational
5. **Medications**: Current medications you're taking
6. **Symptoms**: Any symptoms you're experiencing
7. **Location**: Your current city/state

### 3. Language Selection

Choose from 14 supported languages in the sidebar:
- English (Default)
- Hindi (हिंदी)
- Gujarati (ગુજરાતી)
- Bengali (বাংলা)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Kannada (ಕನ್ನಡ)
- Malayalam (മലയാളം)
- Punjabi (ਪੰਜਾਬੀ)
- Marathi (मराठी)
- Urdu (اردو)
- Assamese (অসমীয়া)
- Odia (ଓଡ଼ିଆ)
- Sanskrit (संस्कृत)

## 🏗️ Architecture

### Core Components

```
├── app.py                 # Main Streamlit application
├── Language Processing    # SUTRA-V2 translation engine
├── AI Response Engine     # Google Gemini integration
├── Memory Management      # Mem0 persistent storage
├── User Interface        # Streamlit frontend
└── Session Management    # User state handling
```

### Data Flow

1. **User Input** → Language Detection → Translation to English
2. **Context Retrieval** → Mem0 searches user history
3. **AI Processing** → Gemini generates response with context
4. **Response Translation** → Back to user's selected language
5. **Memory Storage** → Conversation saved to Mem0

## 🔧 Configuration

### Environment Variables (Optional)
```bash
# If you want to set API keys as environment variables
export SUTRA_API_KEY="your_sutra_api_key"
export MEM0_API_KEY="your_mem0_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
```

### Customization Options

- **Language Addition**: Add new languages to the `languages` list
- **UI Theming**: Modify Streamlit theme in `.streamlit/config.toml`
- **Response Prompts**: Customize AI prompts in `get_chat_response()`
- **Registration Fields**: Modify registration questions array

## 🎯 Usage Examples

### Basic Conversation
```
User: "What should I eat for breakfast?"
Assistant: [Personalized response based on user's diabetes type and location]
```

### Medication Query
```
User: "मुझे मेरी दवा के बारे में जानकारी चाहिए" (Hindi)
Assistant: [Response in Hindi about user's specific medications]
```

### Symptom Reporting
```
User: "I'm feeling dizzy after meals"
Assistant: [Contextual advice based on user's diabetes management plan]
```

## 🔒 Security & Privacy

- **API Key Protection**: Keys are masked in the UI
- **Session Management**: Secure user sessions
- **Data Privacy**: User data stored securely in Mem0
- **No Local Storage**: All data handled server-side

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SUTRA-V2**: Multilingual AI capabilities
- **Google Gemini**: Advanced language processing
- **Mem0**: Persistent memory management
- **Streamlit**: Beautiful web interface
- **Community**: Contributors and users

## 🎉 What's Next?

- [ ] Voice input/output support
- [ ] Medical report analysis
- [ ] Appointment scheduling
- [ ] Family member access
- [ ] Wearable device integration
- [ ] Emergency contact alerts

---

**Made with ❤️ for the diabetes community in India**

*Stay healthy, stay connected!* 🌟
