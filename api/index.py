"""
Vercel serverless API handler for Sunbird AI processing.
Entry point: /api/ routes in Vercel deployment.
"""
import json
import os
from typing import Dict, Any

try:
    from .pipeline import ProcessingPipeline
except ImportError:
    # Fallback for Vercel environment
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pipeline import ProcessingPipeline


def cors_headers() -> Dict[str, str]:
    """Return CORS headers for all responses."""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }


def error_response(message: str, status_code: int = 500) -> tuple:
    """Return standardized error response."""
    return (
        json.dumps({"error": message}),
        status_code,
        cors_headers(),
    )


def success_response(data: Any, status_code: int = 200) -> tuple:
    """Return standardized success response."""
    return (
        json.dumps(data),
        status_code,
        cors_headers(),
    )


def handler(request):
    """Main Vercel serverless function handler."""
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return "", 200, cors_headers()
    
    # Health check endpoint
    if request.path == "/api/health" and request.method == "GET":
        return success_response({"status": "healthy"})
    
    # Process text endpoint
    if request.path == "/api/process-text" and request.method == "POST":
        try:
            data = request.json
            text = data.get("text")
            target_language = data.get("target_language", "luganda")
            
            if not text:
                return error_response("Text input is required", 400)
            
            pipeline = ProcessingPipeline()
            result = pipeline.process_text_input(text, target_language)
            return success_response(result)
            
        except json.JSONDecodeError:
            return error_response("Invalid JSON", 400)
        except Exception as e:
            return error_response(f"Error processing text: {str(e)}", 500)
    
    # Process audio endpoint
    if request.path == "/api/process-audio" and request.method == "POST":
        try:
            # Audio processing via multipart form data
            # Note: requires additional setup for file uploads in Vercel
            return error_response("Audio upload not yet supported", 501)
            
        except Exception as e:
            return error_response(f"Error processing audio: {str(e)}", 500)
    
    # Not found
    return error_response("Endpoint not found", 404)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
