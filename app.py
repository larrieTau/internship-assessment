"""
Sunbird AI GenAI Application
A web app that transcribes audio, summarizes text, translates to Ugandan languages, and synthesizes speech.

Frontend: Gradio
Backend: Sunbird AI API
"""
import os
import gradio as gr
import base64
import io
import numpy as np
import soundfile as sf
from scipy.io import wavfile
from typing import Optional, Tuple
from backend.pipeline import SunbirdPipeline, LANGUAGE_MAPPING
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Initialize pipeline
try:
    pipeline = SunbirdPipeline()
except ValueError as e:
    gr.Warning(f"⚠️ Error: {str(e)}")
    pipeline = None


def convert_audio_bytes_to_gradio_format(audio_bytes: bytes, sample_rate: int = 16000):
    """
    Convert raw audio bytes to Gradio Audio component format.
    Gradio Audio output accepts tuple of (sample_rate, numpy_array).
    """
    try:
        import numpy as np
        import io
        from scipy.io import wavfile
        
        # Create BytesIO from bytes
        buffer = io.BytesIO(audio_bytes)
        
        # Read WAV file
        sr, audio_data = wavfile.read(buffer)
        
        # Normalize audio data to float
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        return (sr, audio_data)
    except Exception as e:
        print(f"Error converting audio: {e}")
        # Fallback: return as-is, Gradio will try to handle
        return None


def process_input(
    input_type: str,
    text_input: str,
    audio_input,
    target_language: str
) -> tuple:
    """
    Main processing function called by Gradio interface.
    
    Args:
        input_type: "text" or "audio"
        text_input: Text input (if text mode)
        audio_input: Audio file tuple (if audio mode)
        target_language: Target language for translation
        
    Returns:
        Tuple of (original_text, summary, translated_summary, audio_output, error_message)
    """
    try:
        if not pipeline:
            return "", "", "", None, "❌ API token not configured. Set SUNBIRD_API_TOKEN."
        
        if not target_language:
            return "", "", "", None, "❌ Please select a target language."
        
        if input_type == "text":
            if not text_input or not text_input.strip():
                return "", "", "", None, "❌ Please enter some text."
            
            results = pipeline.process_text_input(text_input, target_language)
            
            # Convert audio bytes to Gradio format
            audio_output = convert_audio_bytes_to_gradio_format(results["audio_bytes"])
            
            return (
                results["original_text"],
                results["summary"],
                results["translated_summary"],
                audio_output,
                "✅ Processing complete!"
            )
        
        elif input_type == "audio":
            if audio_input is None:
                return "", "", "", None, "❌ Please upload an audio file."
            
            # audio_input is a tuple: (sample_rate, audio_array)
            import numpy as np
            
            sample_rate, audio_array = audio_input
            
            # Convert audio array to WAV bytes
            import soundfile as sf
            
            audio_array = np.array(audio_array)
            if audio_array.ndim == 1:
                # Mono audio
                pass
            elif audio_array.ndim == 2 and audio_array.shape[1] == 1:
                # Stereo with 1 channel
                audio_array = audio_array.flatten()
            
            # Write to BytesIO buffer
            buffer = io.BytesIO()
            sf.write(buffer, audio_array, sample_rate, format='WAV')
            audio_bytes = buffer.getvalue()
            
            # Validate and process
            results = pipeline.process_audio_input(audio_bytes, target_language)
            
            # Convert output audio to Gradio format
            audio_output = convert_audio_bytes_to_gradio_format(results["audio_bytes"])
            
            return (
                results["original_text"],
                results["transcript"] + "\n\n---\n\n" + results["summary"],  # Show transcript in summary
                results["translated_summary"],
                audio_output,
                "✅ Processing complete!"
            )
    
    except ValueError as e:
        # Audio validation errors
        return "", "", "", None, f"❌ Error: {str(e)}"
    except Exception as e:
        return "", "", "", None, f"❌ API Error: {str(e)}"


def create_interface():
    """Create and return the Gradio interface."""
    with gr.Blocks(title="Sunbird AI GenAI App", elem_classes=["app-shell"]) as app:
        gr.Markdown(
            """
            <div class="hero">
              <div class="hero-badge">Sunbird AI Suite</div>
              <h1>🌻 Sunbird AI GenAI Studio</h1>
              <p>
                A premium text and voice intelligence workspace for summarization, translation,
                and speech synthesis in Ugandan local languages.
              </p>
              <div class="hero-pipeline">
                <span>Input</span>
                <span>Transcribe</span>
                <span>Summarize</span>
                <span>Translate</span>
                <span>Synthesize</span>
              </div>
            </div>
            """
        )

        with gr.Row(equal_height=True):
            with gr.Column(scale=5, elem_classes=["panel-card"]):
                gr.Markdown("### Configure Input")
                input_type = gr.Radio(
                    choices=["text", "audio"],
                    value="text",
                    label="Input Type",
                    elem_classes=["control-input-type"]
                )

                target_language = gr.Dropdown(
                    choices=list(LANGUAGE_MAPPING.keys()),
                    value="Luganda",
                    label="Target Language",
                    elem_classes=["control-language"]
                )

                text_input = gr.Textbox(
                    label="Text Input",
                    placeholder="Enter or paste text here...",
                    lines=8,
                    visible=True
                )

                audio_input = gr.Audio(
                    label="Audio Input",
                    type="numpy",
                    visible=False
                )

                process_btn = gr.Button("✨ Process with Sunbird AI", variant="primary", size="lg")
            with gr.Column(scale=4, elem_classes=["panel-card", "tips-panel"]):
                gr.Markdown(
                    """
                    ### Usage Guide
                    - Choose text or audio input mode.
                    - Pick your target Ugandan language.
                    - Click process and review all pipeline outputs.

                    **Supported Languages:** Luganda, Runyankole, Ateso, Lugbara, Acholi.
                    **Audio Limit:** Up to 5 minutes per upload.
                    """
                )

        gr.Markdown("## Results", elem_classes=["results-title"])

        with gr.Row():
            with gr.Column(scale=1, elem_classes=["panel-card"]):
                original_text_output = gr.Textbox(
                    label="📝 Original Text / Transcript",
                    lines=5,
                    interactive=False
                )

                summary_output = gr.Textbox(
                    label="📌 Summary",
                    lines=4,
                    interactive=False
                )

                translated_output = gr.Textbox(
                    label="🌍 Translated Summary",
                    lines=4,
                    interactive=False
                )

                audio_output = gr.Audio(
                    label="🔊 Synthesized Speech",
                    type="numpy",
                    interactive=False
                )

                status_output = gr.Textbox(
                    label="Status",
                    interactive=False,
                    show_label=True
                )

        # Update visibility based on input_type
        def update_input_visibility(choice):
            return (
                gr.Textbox(visible=(choice == "text")),
                gr.Audio(visible=(choice == "audio"))
            )

        input_type.change(
            fn=update_input_visibility,
            inputs=input_type,
            outputs=[text_input, audio_input]
        )

        # Connect process button
        process_btn.click(
            fn=process_input,
            inputs=[input_type, text_input, audio_input, target_language],
            outputs=[
                original_text_output,
                summary_output,
                translated_output,
                audio_output,
                status_output
            ]
        )
    
    return app


if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        share=False,
        theme=gr.themes.Soft(
            primary_hue="emerald",
            secondary_hue="teal",
            neutral_hue="slate",
            spacing_size="md",
            radius_size="lg",
            text_size="md"
        ),
        css="""
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

            body, .gradio-container {
                font-family: 'Inter', sans-serif !important;
                color: #dbe7ff;
                background:
                    radial-gradient(1200px 500px at 8% -10%, rgba(56, 189, 248, 0.26), transparent 58%),
                    radial-gradient(900px 500px at 92% -10%, rgba(34, 197, 94, 0.22), transparent 56%),
                    linear-gradient(145deg, #020617 0%, #0a1022 42%, #101a36 100%);
            }

            .app-shell {
                max-width: 1120px;
                margin: 30px auto !important;
                padding: 0 8px;
            }

            .hero {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at 16% 20%, rgba(56, 189, 248, 0.35), transparent 36%),
                    radial-gradient(circle at 86% 24%, rgba(45, 212, 191, 0.32), transparent 33%),
                    linear-gradient(140deg, #0b1225 0%, #111f42 45%, #1a2f67 100%);
                color: #f8fafc;
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 28px;
                padding: 34px 34px;
                margin-bottom: 20px;
                box-shadow:
                    0 24px 65px rgba(6, 12, 31, 0.55),
                    inset 0 1px 0 rgba(255, 255, 255, 0.18);
            }

            .hero::after {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(100deg, transparent 15%, rgba(255, 255, 255, 0.08) 50%, transparent 80%);
                transform: translateX(-120%);
                animation: hero-shimmer 8s linear infinite;
                pointer-events: none;
            }

            @keyframes hero-shimmer {
                to { transform: translateX(120%); }
            }

            .hero-badge {
                display: inline-block;
                background: rgba(14, 165, 233, 0.2);
                border: 1px solid rgba(103, 232, 249, 0.6);
                border-radius: 999px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.8px;
                text-transform: uppercase;
                color: #dff7ff;
                padding: 7px 13px;
                margin-bottom: 10px;
                box-shadow: 0 8px 22px rgba(14, 165, 233, 0.26);
            }

            .hero h1 {
                font-family: 'Plus Jakarta Sans', sans-serif;
                font-size: clamp(2rem, 4vw, 2.8rem);
                line-height: 1.15;
                letter-spacing: -0.02em;
                margin: 6px 0 12px;
                text-shadow: 0 8px 30px rgba(2, 6, 23, 0.4);
            }

            .hero p {
                color: rgba(219, 234, 254, 0.9);
                font-size: 1.02rem;
                margin-bottom: 18px;
                max-width: 760px;
            }

            .hero-pipeline {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }

            .hero-pipeline span {
                background: rgba(15, 23, 42, 0.45);
                border: 1px solid rgba(125, 211, 252, 0.45);
                border-radius: 999px;
                color: #dff5ff;
                padding: 6px 13px;
                font-size: 12px;
                font-weight: 600;
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12);
            }

            .panel-card {
                background:
                    linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(17, 24, 39, 0.9)),
                    linear-gradient(120deg, rgba(56, 189, 248, 0.08), transparent 40%);
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 22px;
                padding: 18px !important;
                box-shadow:
                    0 20px 45px rgba(1, 6, 22, 0.42),
                    inset 0 1px 0 rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(10px);
            }

            .tips-panel {
                background:
                    linear-gradient(180deg, rgba(13, 31, 60, 0.94), rgba(17, 52, 64, 0.9)),
                    radial-gradient(circle at top right, rgba(45, 212, 191, 0.2), transparent 40%);
            }

            .results-title h2 {
                font-family: 'Plus Jakarta Sans', sans-serif;
                margin: 8px 0 4px;
                color: #e2edff;
                letter-spacing: -0.01em;
            }

            button.primary {
                min-height: 50px !important;
                border: 1px solid rgba(125, 211, 252, 0.35) !important;
                background:
                    linear-gradient(92deg, #06b6d4 0%, #3b82f6 46%, #8b5cf6 100%) !important;
                color: #f8fbff !important;
                font-weight: 700 !important;
                letter-spacing: 0.01em;
                box-shadow:
                    0 15px 35px rgba(59, 130, 246, 0.35),
                    inset 0 1px 0 rgba(255, 255, 255, 0.25);
                transition: transform 0.18s ease, filter 0.25s ease, box-shadow 0.25s ease;
            }

            button.primary:hover {
                transform: translateY(-2px);
                filter: saturate(1.15) brightness(1.04);
                box-shadow:
                    0 20px 44px rgba(59, 130, 246, 0.45),
                    inset 0 1px 0 rgba(255, 255, 255, 0.35);
            }

            .gr-form, .gr-box, .gr-group {
                border-color: rgba(148, 163, 184, 0.26) !important;
                background: rgba(30, 41, 59, 0.55) !important;
            }

            .gradio-container textarea,
            .gradio-container input,
            .gradio-container .wrap {
                border-radius: 14px !important;
                background: rgba(30, 41, 59, 0.86) !important;
                color: #e2e8f0 !important;
                border: 1px solid rgba(148, 163, 184, 0.3) !important;
            }

            .gradio-container textarea:focus,
            .gradio-container input:focus {
                border-color: rgba(56, 189, 248, 0.75) !important;
                box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2) !important;
            }

            .gradio-container label,
            .gradio-container .block-title,
            .gradio-container .prose,
            .gradio-container .prose * {
                color: #d8e7ff !important;
            }

            .gradio-container .prose strong {
                color: #f8fbff !important;
            }

            .gradio-container audio {
                border-radius: 14px;
                background: rgba(15, 23, 42, 0.8);
            }

            @media (max-width: 900px) {
                .hero {
                    padding: 26px 20px;
                    border-radius: 22px;
                }
                .panel-card {
                    padding: 14px !important;
                }
            }
        """
    )
