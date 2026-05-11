"""Audio processing route for Vercel."""
from http.server import BaseHTTPRequestHandler

from ._shared import send_json


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        send_json(
            self,
            {
                "error": "Audio upload is not supported in the Vercel serverless build yet.",
            },
            501,
        )

    def do_OPTIONS(self):
        send_json(self, {"status": "ok"})
