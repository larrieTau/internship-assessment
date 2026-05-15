# Sunbird AI Studio - Complete Setup & Architecture Guide

## System Architecture

The Sunbird AI Studio is built with a modern tech stack designed for seamless content processing:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js + React)                   │
│  - Interactive UI with real-time workflow progress tracking     │
│  - Dark/Light theme support                                     │
│  - Responsive design for all screen sizes                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              API Routes (Next.js API Handler)                   │
│  - /api/process-text (handles text input)                       │
│  - /api/process-audio (handles audio upload)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           Sunbird AI Sunflower Inference Engine                 │
│  - Speech-to-Text (for audio files)                             │
│  - Summarization (both text and transcribed audio)              │
│  - Translation (to 5 Ugandan languages)                         │
│  - Text-to-Speech (synthesis in target language)                │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
internship-assessment/
├── app/
│   ├── api/
│   │   ├── process-text/
│   │   │   └── route.ts          # Text processing API
│   │   ├── process-audio/
│   │   │   └── route.ts          # Audio processing API
│   │   ├── _shared.py            # Shared utilities for API
│   │   └── pipeline.py           # Core pipeline logic
│   ├── page.tsx                  # Main page component
│   ├── layout.tsx                # Root layout
│   └── globals.css               # Global styles
├── public/
│   └── logo.png                  # Sunbird AI logo
├── tests/
│   └── test_basics.py            # Unit tests
├── package.json                  # Node.js dependencies
├── requirements.txt              # Python dependencies
├── tsconfig.json                 # TypeScript config
├── next.config.js                # Next.js config
└── README.md                     # This file
```

## Interactive Workflow Guide

The application features a 5-step guided workflow:

### Step 1: Choose Input Mode
- **Text**: Type or paste content directly
- **Audio**: Upload audio files (MP3, WAV, M4A, etc.)

### Step 2: Set Target Language
- **Available Languages:**
  - Luganda
  - Runyankole
  - Ateso
  - Lugbara
  - Acholi

### Step 3: Add Your Content
- **For Text Mode:** Paste your content (up to several paragraphs)
- **For Audio Mode:** Upload audio file (max 5 minutes recommended)

### Step 4: Review AI Pipeline Output
After clicking "Process", the system generates:
- **Transcript**: Full speech-to-text output (audio only)
- **Summary**: Concise summary of the content
- **Translation**: Summary translated to target language

### Step 5: Play Final Audio
- Listen to the synthesized speech in the target language
- Validate quality before sharing or downloading

## Development Workflow

### Running Locally

1. **Terminal 1 - Start Next.js Frontend**
   ```bash
   npm run dev
   ```
   Frontend runs on: http://localhost:3000

2. **Terminal 2 - Start Python Backend** (if needed)
   ```bash
   python server.py
   # or
   flask run
   ```
   Backend runs on: http://localhost:5000

### API Endpoints

#### POST /api/process-text
Process text content:
```json
{
  "text": "Your content here",
  "target_language": "luganda"
}
```

**Response:**
```json
{
  "pipeline": {
    "transcript": "...",
    "summary": "...",
    "translation": "...",
    "audio": {
      "audio_url": "data:audio/mp3;base64,..."
    }
  }
}
```

#### POST /api/process-audio
Process audio file:
```
multipart/form-data:
- audio: [audio file]
- target_language: "luganda"
```

**Response:**
Same structure as text processing

## Environment Variables

### Required
- `SUNBIRD_API_TOKEN` - Your Sunbird AI API authentication token

### Optional
- `NEXT_PUBLIC_API_URL` - Override API base URL (default: `/api`)
- `NODE_ENV` - Development or production mode

## Building for Production

```bash
# Build the production bundle
npm run build

# Start production server
npm start
```

## Testing

Run the unit tests:
```bash
pytest tests/test_api.py -v
```

## Troubleshooting

### "Connection refused" error
- **Problem:** Backend API not running
- **Solution:** Start the backend server on port 5000

### "No audio generated yet"
- **Problem:** Sunbird API token not set or expired
- **Solution:** Verify `SUNBIRD_API_TOKEN` in `.env.local`

### Audio file too large
- **Problem:** File exceeds 5 minutes
- **Solution:** Trim audio or process multiple files

### Dark mode not persisting
- **Problem:** Browser local storage not enabled
- **Solution:** Check browser privacy settings

## Performance Tips

1. **Optimize Audio Files:** Pre-compress large audio files
2. **Cache Results:** Results are displayed immediately without refresh
3. **Batch Processing:** Process similar content together
4. **Network Speed:** Upload to areas with good connectivity

## Security Considerations

- API tokens are stored in `.env.local` (never commit to git)
- All requests to Sunbird API use HTTPS
- Audio files are processed and not stored on the server
- User data is not logged or stored persistently

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and test thoroughly
3. Commit with clear messages: `git commit -m "Add feature description"`
4. Push to branch: `git push origin feature/your-feature`
5. Create a Pull Request

## Support

For issues or questions:
- Check the README.md for common problems
- Review the Sunbird AI documentation
- Contact the development team

## License

This project is part of the Sunbird AI Internship Assessment program.
