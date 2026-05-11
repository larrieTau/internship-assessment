# Sunbird AI GenAI Application

## 📋 Project Description

This is a generative AI web application powered by **Sunbird AI's Sunflower LLM** and the **Sunbird AI API**. The app accepts either text or audio input, then runs it through an intelligent pipeline to:

1. **Transcribe** audio to text (if audio input)
2. **Summarize** the content using Sunflower LLM
3. **Translate** the summary into a chosen Ugandan local language (Luganda, Runyankole, Ateso, Lugbara, or Acholi)
4. **Synthesize speech** from the translated text using Text-to-Speech
5. **Display** all intermediate results in an intuitive UI

The app is built with a Python backend (Sunbird API client) and a Gradio frontend for easy, no-code deployment.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Input (UI)                         │
│            Text Input ─┬─ Audio Upload                      │
└────────────┬───────────┴─────────────────────────────────────┘
             │
             ▼
    ┌──────────────────────┐
    │  Input Validation    │  (5-min audio check)
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │   STT (if audio)     │  Sunbird Speech-to-Text API
    │  [sunbird_client]    │  Converts audio → transcript
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │  Summarize Text      │  Sunbird Sunflower LLM
    │  [pipeline.py]       │  2-3 sentence summary
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │  Translate Summary   │  Sunbird Sunflower LLM
    │                      │  → Luganda/Runyankole/Ateso/Lugbara/Acholi
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │  TTS Synthesis       │  Sunbird Text-to-Speech API
    │ [sunbird_client]     │  Translated text → audio file
    └──────┬───────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                  Output Display (UI)                         │
│  Original Text | Summary | Translation | Audio Player       │
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Purpose | Endpoints |
|-----------|---------|-----------|
| **SunbirdClient** (`backend/sunbird_client.py`) | Thin wrapper around all Sunbird API endpoints | STT, TTS, Chat (summarize/translate) |
| **SunbirdPipeline** (`backend/pipeline.py`) | Orchestrates the full processing pipeline | Validation, input routing, result collection |
| **Gradio UI** (`app.py`) | Web interface for user interaction | Input/output forms, real-time processing |

---

## 🚀 Local Setup

### Prerequisites
- Python 3.8+
- pip or conda
- Sunbird AI API token (free, from https://sunbird.ai)
- Git

### Step-by-Step Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/internship-assessment.git
cd internship-assessment
```

#### 2. Create Python Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate.bat
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the project root by copying the template:
```bash
cp .env.example .env
```

Edit `.env` and add your Sunbird AI API token:
```
SUNBIRD_API_TOKEN=your_actual_api_token_here
PORT=7860
```

**How to get your Sunbird API token:**
1. Visit https://sunbird.ai
2. Sign up for a free account
3. Go to your API dashboard
4. Generate an API token
5. Copy it into `.env`

#### 5. Run the Application
```bash
python app.py
```

The app will start at `http://localhost:7860`

---

## ⚙️ Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SUNBIRD_API_TOKEN` | **Required.** Your Sunbird AI API token for authentication | `sk_live_a1b2c3d4e5f6...` |
| `PORT` | **Optional.** Port to run the Gradio server on | `7860` (default) |

**Security Note:** Never commit `.env` to git. The `.gitignore` should exclude it.

---

## 📖 Usage

### Text-to-Speech Workflow

1. Open the app at `http://localhost:7860`
2. Select **"text"** input type
3. Paste or type your content in the text box
4. Choose a target language from the dropdown (e.g., Luganda)
5. Click **"🚀 Process"**
6. View results:
   - 📝 Original text
   - 📌 2-3 sentence summary
   - 🌍 Summary translated to your chosen language
   - 🔊 Playable audio of the translated summary

### Audio-to-Speech Workflow

1. Select **"audio"** input type
2. Upload an MP3 or WAV file (max 5 minutes)
3. Choose a target language
4. Click **"🚀 Process"**
5. View results:
   - 📝 Transcript of the audio
   - 📌 Summary of the transcript
   - 🌍 Translated summary
   - 🔊 Audio playback in your chosen language

### Supported Languages

- **Luganda** (lg) — Most widely spoken in Uganda
- **Runyankole** (ny) — Spoken in southwestern Uganda
- **Ateso** (teo) — Spoken in northeastern Uganda
- **Lugbara** (lgg) — Spoken in northwestern Uganda
- **Acholi** (ach) — Spoken in northern Uganda

---

## 🛠️ Project Structure

```
internship-assessment/
├── app.py                          # Gradio frontend entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .env                            # Your local secrets (NOT committed)
├── README.md                       # Original assessment README
├── PROJECT_README.md               # This file
├── constants.py                    # Test constants (Part 1)
├── backend/
│   ├── __init__.py
│   ├── sunbird_client.py           # API client wrapper
│   └── pipeline.py                 # Pipeline orchestrator
├── exercises/                      # Part 1: Programming exercises
│   ├── __init__.py
│   └── basics.py                   # Collatz, distinct_numbers
└── tests/                          # Part 1: Unit tests
    ├── __init__.py
    └── test_basics.py              # 5 passing tests
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `gradio` | ≥4.0.0 | Web UI framework |
| `requests` | Latest | HTTP client for API calls |
| `python-dotenv` | Latest | Load `.env` environment variables |
| `soundfile` | ≥0.12.0 | Audio file I/O |
| `numpy` | ≥1.24.0 | Numerical arrays for audio |
| `scipy` | ≥1.10.0 | Scientific computing (audio processing) |

---

## 🌐 Deployment to Hugging Face Spaces

### Deploy Instructions

#### 1. Create a Hugging Face Account
- Visit https://huggingface.co/join
- Sign up with email or GitHub

#### 2. Create a New Space
- Go to https://huggingface.co/new-space
- **Space name:** `internship-assessment` (or your preferred name)
- **SDK:** Select "Gradio"
- **Visibility:** Select "Public"
- Click "Create Space"

#### 3. Add Sunbird API Token as Secret
- Go to your Space → **Settings** → **Variables and secrets** tab
- Click **"New secret"**
- **Name:** `SUNBIRD_API_TOKEN`
- **Value:** Paste your actual API token
- Click "Add secret"

#### 4. Configure Git Remote and Push
```bash
# In your local repo
git remote add space https://huggingface.co/spaces/<your-username>/<space-name>
git branch -M main  # Ensure you're on main branch
git push -u space main
```

Hugging Face will automatically:
- Build your Docker image
- Install `requirements.txt`
- Start your `app.py`
- Make it publicly accessible

**Your app will be live at:** `https://huggingface.co/spaces/<your-username>/<space-name>`

#### 5. Verify the Deployment
- Open the Space URL in your browser
- Test with sample text or audio
- Confirm all 5 outputs appear correctly

### Deployment Checklist

- ✅ `requirements.txt` lists all dependencies
- ✅ `app.py` is the entry point (Gradio auto-detects it)
- ✅ `.env.example` documents required variables
- ✅ `SUNBIRD_API_TOKEN` is added as a Space secret (not in code)
- ✅ Code doesn't have hardcoded credentials
- ✅ README is updated with deployment link

---

## ⚠️ Known Limitations

1. **Audio Duration:** Files longer than 5 minutes are rejected with an error message
2. **Language Support:** Limited to 5 Ugandan languages (not extensible without code changes)
3. **API Rate Limits:** Sunbird API has rate limits; sustained heavy usage may trigger throttling
4. **Audio Format Support:** Accepts WAV, MP3, OGG; other formats may fail
5. **Transcription Accuracy:** Depends on audio quality; background noise reduces accuracy
6. **Translation Quality:** Translations are LLM-generated and may require manual review for critical use
7. **No Session Persistence:** Results are not saved between page refreshes
8. **No Batch Processing:** Processes one input at a time

---

## 🔧 Troubleshooting

### "SUNBIRD_API_TOKEN not found"
- **Cause:** Environment variable not set
- **Fix:** Create `.env` file (copy from `.env.example`) and add your token

### "Audio file too long"
- **Cause:** Uploaded file exceeds 5 minutes
- **Fix:** Trim the audio to under 5 minutes and retry

### "API Error: 401 Unauthorized"
- **Cause:** Invalid or expired API token
- **Fix:** Verify your token is correct at https://sunbird.ai/api-dashboard

### App won't start
- **Cause:** Missing dependencies
- **Fix:** Run `pip install -r requirements.txt` and ensure venv is activated

### Gradio UI not loading
- **Cause:** Firewall or port already in use
- **Fix:** Try a different port: `python app.py --server_port 8000`

---

## 🧪 Testing

Run the Part 1 programming exercises tests:
```bash
pytest -v
```

Expected output:
```
tests/test_basics.py::test_collatz_1 PASSED
tests/test_basics.py::test_collatz_2 PASSED
tests/test_basics.py::test_collatz_3 PASSED
tests/test_basics.py::test_distinct_numbers_1 PASSED
tests/test_basics.py::test_distinct_numbers_2 PASSED

============================== 5 passed in 0.05s =======================================
```

---

## 📚 API References

- **Sunbird AI Docs:** https://docs.sunbird.ai
- **Speech-to-Text:** https://docs.sunbird.ai/guides/speech-to-text
- **Text-to-Speech:** https://docs.sunbird.ai/guides/text-to-speech
- **Summarisation & Translation:** https://docs.sunbird.ai/guides/sunflower-chat
- **Full API Reference:** https://docs.sunbird.ai/api-reference/introduction

---

## 📝 License

This project is part of the Sunbird AI Internship Assessment. Refer to the original README.md for licensing terms.

---

## ✅ Submission Checklist

- ✅ Part 1: All 5 tests passing (`pytest`)
- ✅ Part 2: GenAI app with full pipeline (STT → Summarize → Translate → TTS)
- ✅ Part 3: README with setup, architecture, and deployment
- ✅ Deployed to Hugging Face Spaces (public URL)
- ✅ GitHub repository with PR (or repository link)
- ✅ `.env.example` documents all required env vars
- ✅ No hardcoded API keys in code

---

**Questions or issues?** Refer to the Sunbird AI documentation or reach out to support@sunbird.ai.
