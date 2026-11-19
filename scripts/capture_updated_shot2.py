import os
import sys
import time
import threading
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app

class ServerThread(threading.Thread):
    def __init__(self, flask_app, port=5000):
        super().__init__()
        self.server = make_server("127.0.0.1", port, flask_app)
        self.ctx = flask_app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

def capture():
    server = ServerThread(app, 5000)
    server.start()
    time.sleep(1.0)
    
    screenshots_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))
    os.makedirs(screenshots_dir, exist_ok=True)
    out_file = os.path.join(screenshots_dir, "landing-shot-2-updated-cards.png")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--use-gl=angle",
                    "--use-angle=swiftshader",
                    "--enable-unsafe-swiftshader",
                    "--disable-web-security"
                ]
            )
            page = browser.new_page(viewport={"width": 1600, "height": 900})
            print("Navigating to /?shot=2...")
            page.goto("http://127.0.0.1:5000/?shot=2")
            
            start = time.time()
            done = False
            while time.time() - start < 45.0:
                is_done = page.evaluate("() => document.getElementById('pre') && document.getElementById('pre').classList.contains('done')")
                if is_done:
                    done = True
                    break
                time.sleep(0.5)
            
            print(f"Preloader finished: {done} (elapsed: {time.time() - start:.1f}s)")
            time.sleep(1.0)
            page.screenshot(path=out_file)
            print(f"Saved: {out_file} ({os.path.getsize(out_file)} bytes)")
            browser.close()
    finally:
        server.shutdown()

if __name__ == "__main__":
    capture()
