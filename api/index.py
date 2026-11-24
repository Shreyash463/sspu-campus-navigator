import sys
import os

# Ensure project root is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Ensure working directory is root_dir for relative assets and database
os.chdir(root_dir)

from app import app

class VercelPathFixer:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # When Vercel rewrites routes to /api/index, restore the original incoming path
        matched = environ.get('HTTP_X_MATCHED_PATH') or environ.get('REQUEST_URI') or environ.get('RAW_URI')
        if matched:
            environ['PATH_INFO'] = matched.split('?')[0]
        elif environ.get('PATH_INFO') in ('/api/index', '/api/index.py', '/api'):
            environ['PATH_INFO'] = '/'
        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixer(app.wsgi_app)
