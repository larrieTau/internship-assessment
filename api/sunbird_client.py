"""
Thin wrapper around Sunbird AI API endpoints.
Handles authentication and request/response formatting.
"""
import base64
import math
import os
import requests
import struct
import wave
from io import BytesIO
from typing import Optional, Dict, Any

class SunbirdClient:
    """Client for interacting with Sunbird AI APIs."""
    
    BASE_URL = "https://api.sunbird.ai"

    @staticmethod
    def _mock_tts_data_uri(duration_seconds: float = 1.0, sample_rate: int = 22050) -> str:
        """Generate a short WAV tone as a data URI for mock-mode playback."""
        amplitude = 0.3
        frequency_hz = 440.0
        total_samples = int(sample_rate * duration_seconds)

        pcm = BytesIO()
        with wave.open(pcm, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            for n in range(total_samples):
                value = amplitude * math.sin(2.0 * math.pi * frequency_hz * (n / sample_rate))
                sample = int(max(-1.0, min(1.0, value)) * 32767)
                wav_file.writeframes(struct.pack("<h", sample))

        encoded = base64.b64encode(pcm.getvalue()).decode("ascii")
        return f"data:audio/wav;base64,{encoded}"
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize with API token from environment or parameter."""
        self.api_token = api_token or os.getenv("SUNBIRD_API_TOKEN")
        self.mock = False
        if not self.api_token:
            # Operate in mock mode when no API token is provided to avoid crashing
            # This allows local testing without requiring access to Sunbird APIs.
            self.mock = True
            self.headers = {}
        else:
            self.headers = {
                "Authorization": f"Bearer {self.api_token}"
            }
    
    def _extract_text(self, response: Dict[str, Any], fallback: str = "") -> str:
        if not isinstance(response, dict):
            return fallback

        if response.get("response"):
            return response.get("response")

        if response.get("text"):
            return response.get("text")

        if response.get("translation"):
            return response.get("translation")

        if response.get("summary"):
            return response.get("summary")

        output = response.get("output")
        if isinstance(output, dict):
            if output.get("text"):
                return output.get("text")
            if output.get("translation"):
                return output.get("translation")
        if isinstance(output, str):
            return output

        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            first_choice = choices[0]
            if isinstance(first_choice, dict) and first_choice.get("text"):
                return first_choice.get("text")
            if isinstance(first_choice, str):
                return first_choice

        return fallback
    
    def transcribe(self, audio_file_path: str, language: str = "eng") -> Dict[str, Any]:
        """
        Transcribe audio file to text using Speech-to-Text API.
        """
        if self.mock:
            # Return a simple mock transcription
            return {"output": {"text": "(mock) transcribed text from audio"}}

        url = f"{self.BASE_URL}/tasks/stt"
        with open(audio_file_path, 'rb') as f:
            files = {'audio': f}
            response = requests.post(url, headers=self.headers, files=files)
            response.raise_for_status()
            return response.json()
    
    def summarize(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Summarize text using Sunflower Simple inference.
        """
        if self.mock:
            # Return a trivial mock summary (first 120 chars)
            return {"summary": text[:120]}

        url = f"{self.BASE_URL}/tasks/sunflower_simple"
        payload = {
            "instruction": f"Summarize the following text concisely:\n\n{text}",
            "model_type": "qwen",
            "temperature": 0.3
        }
        response = requests.post(url, headers=self.headers, data=payload)
        response.raise_for_status()
        return response.json()
    
    def translate(self, text: str, target_language: str) -> Dict[str, Any]:
        """
        Translate text to a target language.
        """
        # Map language codes to full names for the instruction
        language_names = {
            "lug": "Luganda",
            "nyn": "Runyankole", 
            "teo": "Ateso",
            "lgg": "Lugbara",
            "ach": "Acholi"
        }
        
        target_name = language_names.get(target_language, target_language)
        
        if self.mock:
            # Mock translation by appending a note about target language
            return {"translation": f"(mock translation to {target_name}) {text}"}

        url = f"{self.BASE_URL}/tasks/sunflower_simple"
        payload = {
            "instruction": f"Translate '{text}' to {target_name}",
            "model_type": "qwen",
            "temperature": 0.1
        }
        response = requests.post(url, headers=self.headers, data=payload)
        response.raise_for_status()
        return response.json()
    
    def text_to_speech(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Generate audio from text using Text-to-Speech API.
        """
        if self.mock:
            # In mock mode, return a playable data URI so the audio section still functions.
            return {
                "audio_url": self._mock_tts_data_uri(),
                "message": "Mock mode is enabled. Add SUNBIRD_API_TOKEN to generate playable audio.",
                "mock": True,
            }

        url = f"{self.BASE_URL}/tasks/modal/tts"
        payload = {
            "text": text,
            "response_mode": "url"
        }
        response = requests.post(url, headers={**self.headers, "Content-Type": "application/json"}, json=payload)
        response.raise_for_status()
        return response.json()
    
    def summarize_text(self, text: str) -> str:
        return self._extract_text(self.summarize(text), text[:100])

    def translate_text(self, text: str, target_language: str) -> str:
        return self._extract_text(self.translate(text, target_language), text)
