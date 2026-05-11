"""Text processing route for Vercel."""
import json
from http.server import BaseHTTPRequestHandler

from ._shared import load_pipeline, read_json_body, send_json


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            data = read_json_body(self)
            text = data.get("text")
            target_language = data.get("target_language", "luganda")

            if not text:
                send_json(self, {"error": "Text input is required"}, 400)
                return

            pipeline = load_pipeline()
            result = pipeline.process_text_input(text, target_language)
            send_json(self, result)
        except json.JSONDecodeError:
            send_json(self, {"error": "Invalid JSON"}, 400)
        except Exception as exc:
            send_json(self, {"error": f"Error processing text: {exc}"}, 500)

    def do_OPTIONS(self):
        send_json(self, {"status": "ok"})
