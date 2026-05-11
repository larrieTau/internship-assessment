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

            body, .gradio-container {
                font-family: 'Inter', sans-serif !important;
                background: radial-gradient(circle at 10% 10%, #dcfce7 0%, #f8fafc 45%, #eff6ff 100%);
            }

            .app-shell {
                max-width: 1050px;
                margin: 24px auto !important;
            }

            .hero {
                background: linear-gradient(135deg, #0f172a 0%, #14532d 55%, #0e7490 100%);
                color: #f8fafc;
                border-radius: 20px;
                padding: 26px 30px;
                margin-bottom: 18px;
                box-shadow: 0 20px 45px rgba(15, 23, 42, 0.25);
            }

            .hero-badge {
                display: inline-block;
                background: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 999px;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.6px;
                text-transform: uppercase;
                padding: 6px 12px;
                margin-bottom: 8px;
            }

            .hero h1 {
                font-size: 2rem;
                line-height: 1.15;
                margin: 6px 0 10px;
            }

            .hero p {
                color: rgba(241, 245, 249, 0.95);
                font-size: 1rem;
                margin-bottom: 14px;
                max-width: 780px;
            }

            .hero-pipeline {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }

            .hero-pipeline span {
                background: rgba(248, 250, 252, 0.14);
                border: 1px solid rgba(248, 250, 252, 0.25);
                border-radius: 999px;
                padding: 5px 12px;
                font-size: 12px;
                font-weight: 500;
            }

            .panel-card {
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid rgba(148, 163, 184, 0.28);
                border-radius: 16px;
                padding: 14px !important;
                box-shadow: 0 10px 30px rgba(2, 6, 23, 0.07);
                backdrop-filter: blur(8px);
            }

            .tips-panel {
                background: linear-gradient(180deg, rgba(226, 232, 240, 0.7), rgba(240, 253, 244, 0.75));
            }

            .results-title h2 {
                margin: 4px 0 2px;
                color: #0f172a;
            }

            button.primary {
                background: linear-gradient(90deg, #16a34a, #0891b2) !important;
                border: none !important;
                box-shadow: 0 8px 24px rgba(8, 145, 178, 0.28);
                transition: transform 0.15s ease, filter 0.2s ease;
            }

            button.primary:hover {
                transform: translateY(-1px);
                filter: saturate(1.08);
            }

            .gradio-container textarea,
            .gradio-container input,
            .gradio-container .wrap {
                border-radius: 12px !important;
            }
        """
    )
