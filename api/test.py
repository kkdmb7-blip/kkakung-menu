from http.server import BaseHTTPRequestHandler
import json
import os
import traceback
import importlib.util
import io

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        result = {}
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)

            spec = importlib.util.spec_from_file_location(
                "menu_image",
                os.path.join(os.path.dirname(__file__), 'menu-image.py')
            )
            mi = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mi)

            png = mi.make_yushik_image(data)

            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(png)))
            self.end_headers()
            self.wfile.write(png)
            return
        except Exception as e:
            result['error'] = str(e)
            result['trace'] = traceback.format_exc()

        body_out = json.dumps(result, ensure_ascii=False).encode('utf-8')
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body_out)))
        self.end_headers()
        self.wfile.write(body_out)
