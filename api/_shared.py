"""Shared helpers for Vercel Python route handlers."""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict


def cors_headers() -> Dict[str, str]:
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }


def send_json(handler: BaseHTTPRequestHandler, payload: Any, status_code: int = 200) -> None:
    handler.send_response(status_code)
    for key, value in cors_headers().items():
        handler.send_header(key, value)
    handler.end_headers()
    handler.wfile.write(json.dumps(payload).encode("utf-8"))


def read_json_body(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    content_length = int(handler.headers.get("Content-Length", 0))
    if content_length <= 0:
        return {}

    raw_body = handler.rfile.read(content_length).decode("utf-8")
    if not raw_body.strip():
        return {}

    return json.loads(raw_body)


def load_pipeline():
    try:
        from .pipeline import ProcessingPipeline
    except ImportError:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from pipeline import ProcessingPipeline

    return ProcessingPipeline()
