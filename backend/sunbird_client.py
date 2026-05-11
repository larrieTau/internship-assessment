"""
Thin wrapper around Sunbird AI API endpoints.
Reference: https://docs.sunbird.ai/api-reference/introduction
"""
import os
import requests
from typing import Optional, Tuple
import io
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class SunbirdClient:
    """Client for Sunbird AI API endpoints."""
    
    BASE_URL = "https://api.sunbird.ai"
    TTS_SPEAKER_BY_LANGUAGE = {
        "ach": 241,
        "teo": 242,
        "nyn": 243,
        "lgg": 245,
        "swa": 246,
        "lug": 248,
        # Common aliases used in this project/configs
        "en": 248,
        "eng": 248,
        "lg": 248,
        "ny": 243,
    }
    
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
        # Avoid accidental corporate/system proxy interference with Sunbird API calls.
        self.session = requests.Session()
        self.session.trust_env = False
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.8,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _headers_without_content_type(self) -> dict:
        """Return auth headers for form/multipart requests."""
        return {k: v for k, v in self.headers.items() if k != "Content-Type"}

    def _raise_for_status_with_context(self, response: requests.Response, action: str) -> None:
        """Raise detailed errors so UI can surface actionable API issues."""
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            body_preview = response.text[:300] if response.text else ""
            raise requests.HTTPError(
                f"{action} failed ({response.status_code}): {body_preview}",
                response=response
            ) from exc
    
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
        url = f"{self.BASE_URL}/tasks/stt"
        files = {"audio": ("audio.wav", io.BytesIO(audio_bytes), "audio/wav")}
        
        # Remove Content-Type from headers for multipart form data
        headers = self._headers_without_content_type()
        
        params = {"language": language_code}
        
        response = self.session.post(url, files=files, headers=headers, params=params, timeout=(10, 90))
        self._raise_for_status_with_context(response, "Speech-to-Text request")
        
        data = response.json()
        output = data.get("output", {})
        return output.get("text") or data.get("transcript", "")

    def _extract_chat_content(self, data: dict) -> str:
        """Extract text from Sunbird chat/simple response shapes."""
        output = data.get("output")
        if isinstance(output, dict):
            if output.get("content"):
                return output["content"]
            if output.get("text"):
                return output["text"]
        if data.get("response"):
            return data["response"]
        # Backward-compatible shape
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    
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
        url = f"{self.BASE_URL}/tasks/sunflower_simple"
        
        prompt = f"Summarize the following text in 2-3 sentences:\n\n{text}"
        
        payload = {"instruction": prompt}
        
        response = self.session.post(
            url,
            data=payload,
            headers=self._headers_without_content_type(),
            timeout=(10, 90)
        )
        self._raise_for_status_with_context(response, "Sunflower summarization request")
        
        data = response.json()
        return self._extract_chat_content(data)
    
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
        url = f"{self.BASE_URL}/tasks/sunflower_simple"
        
        prompt = f"Translate the following text to {target_language}. Only provide the translation, no explanation:\n\n{text}"
        
        payload = {"instruction": prompt}
        
        response = self.session.post(
            url,
            data=payload,
            headers=self._headers_without_content_type(),
            timeout=(10, 90)
        )
        self._raise_for_status_with_context(response, "Sunflower translation request")
        
        data = response.json()
        return self._extract_chat_content(data)
    
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
        url = f"{self.BASE_URL}/tasks/tts"
        speaker_id = self.TTS_SPEAKER_BY_LANGUAGE.get(language_code, 248)

        payload = {
            "text": text,
            "speaker_id": speaker_id
        }

        response = self.session.post(url, json=payload, headers=self.headers, timeout=(10, 90))
        self._raise_for_status_with_context(response, "Text-to-Speech request")
        data = response.json()

        # New API returns an audio URL
        audio_url = data.get("output", {}).get("audio_url")
        if audio_url:
            audio_resp = self.session.get(audio_url, timeout=(10, 90))
            self._raise_for_status_with_context(audio_resp, "Audio download")
            return audio_resp.content, audio_resp.headers.get("Content-Type", "audio/wav")

        # Fallback for any direct-byte responses
        return response.content, response.headers.get("Content-Type", "audio/wav")
