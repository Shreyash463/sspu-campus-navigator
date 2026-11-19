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
        page.on("console", lambda m: print("CONSOLE:", m.text))
        print("Navigating to ?shot=0 ...")
        page.goto("http://127.0.0.1:5000/?shot=0")
        for i in range(15):
            time.sleep(0.5)
            info = page.evaluate("() => ({ pre: document.getElementById('pre') ? document.getElementById('pre').className : 'null', kage: Boolean(window.__kage) })")
            print(f"Tick {i}: {info}")
            if "done" in info["pre"]:
                print("Shot 0 loaded done!")
                break
        browser.close()
finally:
    s.shutdown()
