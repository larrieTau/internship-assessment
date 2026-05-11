"""Health check route for Vercel."""
from http.server import BaseHTTPRequestHandler

from ._shared import send_json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        send_json(self, {"status": "healthy"})

    def do_OPTIONS(self):
        send_json(self, {"status": "healthy"})
