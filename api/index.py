import sys
import os
import json

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

os.chdir(root_dir)

from app import app

class VercelPathFixer:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Print environ headers to stderr for instant inspection in vercel logs
        headers_info = {k: str(v) for k, v in environ.items() if not k.startswith("wsgi.")}
        print("VERCEL_WSGI_ENVIRON:", json.dumps(headers_info), file=sys.stderr, flush=True)

        # Check all possible path variables
        real_path = (
            environ.get('HTTP_X_FORWARDED_PATH') or
            environ.get('HTTP_X_MATCHED_PATH') or
            environ.get('HTTP_X_VERCEL_REQUEST_URI') or
            environ.get('REQUEST_URI') or
            environ.get('RAW_URI')
        )
        if real_path:
            environ['PATH_INFO'] = real_path.split('?')[0]
        elif environ.get('PATH_INFO') in ('/api/index', '/api/index.py', '/api'):
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixer(app.wsgi_app)
