from http.server import BaseHTTPRequestHandler
import json
import os
import traceback
import importlib.util

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        result = {}
        try:
            spec = importlib.util.spec_from_file_location(
                "menu_image",
                os.path.join(os.path.dirname(__file__), 'menu-image.py')
            )
            mi = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mi)
            result['import'] = 'ok'

            data = {
                "type": "yushik",
                "date_str": "test",
                "menus": [
                    {"name": "t1", "ingred": ["a, b", "c, d"]},
                    {"name": "t2", "ingred": ["e, f", "g, h"]},
                    {"name": "t3", "ingred": ["i, j", "k, l"]}
                ],
                "origins": ""
            }
            png = mi.make_yushik_image(data)
            result['png_size'] = len(png)
            result['status'] = 'ok'
        except Exception as e:
            result['error'] = str(e)
            result['trace'] = traceback.format_exc()

        body = json.dumps(result, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
