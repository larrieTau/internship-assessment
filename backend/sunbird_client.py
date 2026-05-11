"""
Thin wrapper around Sunbird AI API endpoints.
Reference: https://docs.sunbird.ai/api-reference/introduction
"""
import os
import requests
from typing import Optional, Tuple
import io


class SunbirdClient:
    """Client for Sunbird AI API endpoints."""
    
    BASE_URL = "https://api.sunbird.ai/v1"
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Sunbird client with API token.
        
        Args:
            api_token: Sunbird API token. If None, reads from SUNBIRD_API_TOKEN env var.
        """
        self.api_token = api_token or os.getenv("SUNBIRD_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "SUNBIRD_API_TOKEN not found. Set env var or pass api_token parameter."
            )
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
    
    def speech_to_text(self, audio_bytes: bytes, language_code: str = "en") -> str:
        """
        Transcribe audio to text using Sunbird Speech-to-Text API.
        
        Args:
            audio_bytes: Audio file bytes (WAV, MP3, etc.)
            language_code: Language code (e.g., 'en', 'lg' for Luganda)
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/speech_recognition"
        files = {"file": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav")}
        
        # Remove Content-Type from headers for multipart form data
        headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        
        params = {"language": language_code}
        
        response = requests.post(url, files=files, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get("transcript", "")
    
    def summarize(self, text: str) -> str:
        """
        Summarize text using Sunflower LLM.
        
        Args:
            text: Text to summarize
            
        Returns:
            Summarized text
            
        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/chat"
        
        prompt = f"Summarize the following text in 2-3 sentences:\n\n{text}"
        
        payload = {
            "model": "sunflower",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def translate(self, text: str, target_language: str) -> str:
        """
        Translate text to target language using Sunflower LLM.
        
        Args:
            text: Text to translate
            target_language: Target language name (e.g., 'Luganda', 'Runyankole', 'Ateso', 'Lugbara', 'Acholi')
            
        Returns:
            Translated text
            
        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/chat"
        
        prompt = f"Translate the following text to {target_language}. Only provide the translation, no explanation:\n\n{text}"
        
        payload = {
            "model": "sunflower",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def text_to_speech(self, text: str, language_code: str = "en") -> Tuple[bytes, str]:
        """
        Generate speech audio from text using Sunbird Text-to-Speech API.
        
        Args:
            text: Text to synthesize
            language_code: Language code (e.g., 'en', 'lg' for Luganda)
            
        Returns:
            Tuple of (audio_bytes, mime_type)
            
        Raises:
            Exception: If API call fails
        """
        url = f"{self.BASE_URL}/text_to_speech"
        
        payload = {
            "text": text,
            "language": language_code
        }
        
        response = requests.post(url, json=payload, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        # Return raw audio bytes and mime type
        return response.content, response.headers.get("Content-Type", "audio/wav")
