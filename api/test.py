from http.server import BaseHTTPRequestHandler
import json
import os
import traceback

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        result = {}
        try:
            from PIL import Image, ImageDraw, ImageFont
            result['pillow'] = 'ok'
            font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NanumGothic-Regular.ttf')
            f = ImageFont.truetype(font_path, 14)
            result['font'] = 'ok'
            img = Image.new('RGB', (100, 100), (255,255,255))
            draw = ImageDraw.Draw(img)
            draw.text((10,10), '테스트', fill=(0,0,0), font=f)
            result['draw'] = 'ok'
        except Exception as e:
            result['error'] = str(e)
            result['trace'] = traceback.format_exc()

        body = json.dumps(result, ensure_ascii=False).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
