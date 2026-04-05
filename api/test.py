from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        files = os.listdir(font_dir) if os.path.exists(font_dir) else ['DIR NOT FOUND']
        body = json.dumps({
            'file': __file__,
            'font_dir': font_dir,
            'fonts': files
        }).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
