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
    
    with gr.Blocks(title="Sunbird AI GenAI App") as app:
        
        gr.Markdown("""
        # 🌻 Sunbird AI GenAI Application
        
        Transform text and audio through AI-powered summarization, translation, and speech synthesis.
        
        **Pipeline:** Input → (Transcribe if audio) → Summarize → Translate → Synthesize Speech
        """)
        
        with gr.Group():
            input_type = gr.Radio(
                choices=["text", "audio"],
                value="text",
                label="Input Type"
            )
            
            target_language = gr.Dropdown(
                choices=list(LANGUAGE_MAPPING.keys()),
                value="Luganda",
                label="Target Language"
            )
        
        # Conditional inputs based on input_type
        with gr.Group():
            text_input = gr.Textbox(
                label="Text Input",
                placeholder="Enter or paste text here...",
                lines=5,
                visible=True
            )
            
            audio_input = gr.Audio(
                label="Audio Input",
                type="numpy",
                visible=False
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
        
        # Process button
        process_btn = gr.Button("🚀 Process", variant="primary", size="lg")
        
        # Output section
        gr.Markdown("### Results")
        
        with gr.Group():
            original_text_output = gr.Textbox(
                label="📝 Original Text / Transcript",
                lines=4,
                interactive=False
            )
            
            summary_output = gr.Textbox(
                label="📌 Summary",
                lines=3,
                interactive=False
            )
            
            translated_output = gr.Textbox(
                label="🌍 Translated Summary",
                lines=3,
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
        
        # Example usage
        gr.Markdown("""
        ---
        ### 📚 How it works
        
        1. **Choose Input**: Select text or audio
        2. **Pick Language**: Choose your target Ugandan language (Luganda, Runyankole, Ateso, Lugbara, Acholi)
        3. **Process**: Click the button
        4. **Review Results**: See transcript/text, summary, translation, and hear the audio
        
        **Supported Languages:**
        - Luganda
        - Runyankole
        - Ateso
        - Lugbara
        - Acholi
        
        **Constraints:**
        - Audio files limited to 5 minutes
        - Powered by Sunbird AI's Sunflower LLM
        """)
    
    return app


if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),
        share=False,
        theme=gr.themes.Soft(),
        css="""
            .tab-nav { margin-bottom: 10px; }
            .container { max-width: 900px; margin: 0 auto; }
        """
    )
