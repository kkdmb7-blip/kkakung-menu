from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
import urllib.parse

SB_URL = os.environ.get('SB_URL', 'https://ymghmfkqctckxxysxkvy.supabase.co')
SB_SERVICE_KEY = os.environ.get('SB_SERVICE_KEY', '')
MENU_PASSWORD = os.environ.get('MENU_PASSWORD', '')


def _sb(method, path, body=None):
    url = f"{SB_URL}/rest/v1/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header('apikey', SB_SERVICE_KEY)
    req.add_header('Authorization', f'Bearer {SB_SERVICE_KEY}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Prefer', 'resolution=merge-duplicates,return=minimal')
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


class handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
        except Exception:
            return self._send(400, {'error': 'bad request'})

        # 서버 설정 확인
        if not SB_SERVICE_KEY or not MENU_PASSWORD:
            return self._send(500, {'error': 'server not configured (env missing)'})

        # 비밀번호 검증
        if str(data.get('password', '')) != MENU_PASSWORD:
            return self._send(401, {'error': '비밀번호가 틀렸습니다'})

        action = data.get('action')

        try:
            if action == 'upsert':
                row = data.get('row')
                if not isinstance(row, dict) or not row.get('id'):
                    return self._send(400, {'error': 'invalid row'})
                code, txt = _sb('POST', 'kkakung_history', row)
                if code >= 300:
                    return self._send(502, {'error': f'db {code}: {txt[:200]}'})
                return self._send(200, {'ok': True})

            if action == 'delete':
                wid = str(data.get('id', ''))
                if not wid:
                    return self._send(400, {'error': 'id required'})
                code, txt = _sb('DELETE', f'kkakung_history?id=eq.{urllib.parse.quote(wid)}')
                if code >= 300:
                    return self._send(502, {'error': f'db {code}: {txt[:200]}'})
                return self._send(200, {'ok': True})

            return self._send(400, {'error': 'unknown action'})
        except Exception as e:
            return self._send(500, {'error': f'{type(e).__name__}: {str(e)[:200]}'})
