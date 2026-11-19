import os, sys, time, threading
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app

class ServerThread(threading.Thread):
    def __init__(self, app, port=5000):
        super().__init__()
        self.server = make_server("127.0.0.1", port, app)
    def run(self):
        self.server.serve_forever()
    def shutdown(self):
        self.server.shutdown()

s = ServerThread(app, 5000)
s.start()
time.sleep(1)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--use-angle=swiftshader",
            "--enable-unsafe-swiftshader",
            "--ignore-gpu-blocklist"
        ])
        page = browser.new_page()
        page.goto("http://127.0.0.1:5000/")
        # Poll for #pre class
        for i in range(20):
            time.sleep(0.5)
            pre_cls = page.evaluate("() => document.getElementById('pre') ? document.getElementById('pre').className : 'none'")
            kage_info = page.evaluate("() => window.__kage ? (window.__kage.fallback ? 'fallback' : 'live_webgl') : 'none'")
            print(f"Tick {i}: pre class='{pre_cls}', window.__kage='{kage_info}'")
            if "done" in pre_cls:
                print("FOUND done!")
                break
        browser.close()
finally:
    s.shutdown()
