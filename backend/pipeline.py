"""
Pipeline orchestrator for the Sunbird AI application.
Coordinates STT -> Summarize -> Translate -> TTS flow.
"""
import os
import io
from typing import Optional, Dict, Tuple
from backend.sunbird_client import SunbirdClient


LANGUAGE_MAPPING = {
    "Luganda": "lug",
    "Runyankole": "nyn",
    "Ateso": "teo",
    "Lugbara": "lgg",
    "Acholi": "ach",
}


class SunbirdPipeline:
    """Orchestrates the complete AI pipeline."""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize pipeline with Sunbird client.
        
        Args:
            api_token: Sunbird API token (optional, reads from env if not provided)
        """
        self.client = SunbirdClient(api_token)
    
    def validate_audio(self, audio_bytes: bytes, max_duration_seconds: int = 300) -> Tuple[bool, Optional[str]]:
        """
        Validate audio file constraints.
        
        Args:
            audio_bytes: Audio file bytes
            max_duration_seconds: Maximum allowed duration (default 5 min = 300s)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Rough estimation: 1 second of audio ≈ 44,100 * 2 bytes (44.1kHz, 16-bit)
        # This is approximate and varies by format
        bytes_per_second = 88200  # Rough average
        estimated_seconds = len(audio_bytes) / bytes_per_second
        
        if estimated_seconds > max_duration_seconds:
            return False, f"Audio file too long ({estimated_seconds:.1f}s). Maximum: {max_duration_seconds}s (5 minutes)."
        
        return True, None
    
    def process_text_input(
        self,
        text: str,
        target_language: str
    ) -> Dict[str, str]:
        """
        Process text input through the pipeline (summarize -> translate -> TTS).
        
        Args:
            text: Input text
            target_language: Target language for translation (e.g., 'Luganda')
            
        Returns:
            Dict with keys: original_text, summary, translated_summary, audio_base64
            
        Raises:
            Exception: If any API call fails
        """
        results = {}
        
        # Original text
        results["original_text"] = text
        
        # Summarize
        results["summary"] = self.client.summarize(text)
        
        # Translate
        results["translated_summary"] = self.client.translate(results["summary"], target_language)
        
        # Text-to-Speech
        target_lang_code = LANGUAGE_MAPPING.get(target_language, "en")
        audio_bytes, _ = self.client.text_to_speech(results["translated_summary"], target_lang_code)
        results["audio_bytes"] = audio_bytes
        
        return results
    
    def process_audio_input(
        self,
        audio_bytes: bytes,
        target_language: str
    ) -> Dict[str, str]:
        """
        Process audio input through the full pipeline (STT -> summarize -> translate -> TTS).
        
        Args:
            audio_bytes: Audio file bytes
            target_language: Target language for translation
            
        Returns:
            Dict with keys: transcript, original_text, summary, translated_summary, audio_base64
            
        Raises:
            Exception: If any API call fails or audio validation fails
        """
        # Validate audio duration
        is_valid, error = self.validate_audio(audio_bytes)
        if not is_valid:
            raise ValueError(error)
        
        results = {}
        
        # Speech-to-Text
        results["transcript"] = self.client.speech_to_text(audio_bytes, "en")
        results["original_text"] = results["transcript"]
        
        # Summarize
        results["summary"] = self.client.summarize(results["transcript"])
        
        # Translate
        results["translated_summary"] = self.client.translate(results["summary"], target_language)
        
        # Text-to-Speech
        target_lang_code = LANGUAGE_MAPPING.get(target_language, "en")
        audio_bytes_output, _ = self.client.text_to_speech(results["translated_summary"], target_lang_code)
        results["audio_bytes"] = audio_bytes_output
        
        return results
