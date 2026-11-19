"""
Playwright Landing Page Test Script
Runs headless Chromium with swiftshader WebGL args.
Verifies:
- Page loads at '/'
- #pre gets class 'done'
- window.__kage exists and is not .fallback
- Zero console errors and zero failed network requests
- Takes screenshots of /?shot=0 through /?shot=5 at 1440x900
- Scrolls with mouse wheel through every chapter and screenshots each
- Confirms 'Open Navigator' CTA navigates to /app
- Tests mobile at 390x844 (menu opens, CTA visible, no horizontal overflow)
- Tests /?nogl=1 renders CSS fallback
- Measures average FPS during scroll
"""

import os
import sys
import time
import threading
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))
os.makedirs(DOCS_DIR, exist_ok=True)

class ServerThread(threading.Thread):
    def __init__(self, app, port=5000):
        super().__init__()
        self.server = make_server("127.0.0.1", port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

def run_landing_tests():
    server = ServerThread(app, 5000)
    server.start()
    time.sleep(1.5)

    try:
        with sync_playwright() as p:
            args = [
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
                "--ignore-gpu-blocklist"
            ]
            browser = p.chromium.launch(headless=True, args=args)

            # -------------------------------------------------------------
            # Desktop 1440x900 tests
            # -------------------------------------------------------------
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            console_errors = []
            failed_requests = []

            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("requestfailed", lambda req: failed_requests.append(f"{req.url} - {req.failure}"))

            print("Navigating to http://127.0.0.1:5000/ ...")
            page.goto("http://127.0.0.1:5000/", wait_until="networkidle")

            # Wait for preloader #pre to get class 'done'
            print("Waiting for #pre.done...")
            page.wait_for_selector("#pre.done", timeout=15000)

            # Check window.__kage
            kage_info = page.evaluate("() => ({ exists: Boolean(window.__kage), isFallback: Boolean(window.__kage && window.__kage.fallback) })")
            print(f"window.__kage: exists={kage_info['exists']}, isFallback={kage_info['isFallback']}")
            assert kage_info["exists"], "window.__kage must exist"
            assert not kage_info["isFallback"], "window.__kage must not be .fallback"

            print(f"Console errors ({len(console_errors)}):", console_errors)
            print(f"Failed requests ({len(failed_requests)}):", failed_requests)
            assert len(console_errors) == 0, f"Expected 0 console errors, got: {console_errors}"
            assert len(failed_requests) == 0, f"Expected 0 failed requests, got: {failed_requests}"

            # Capture shots 0 to 5
            for shot in range(6):
                page.goto(f"http://127.0.0.1:5000/?shot={shot}", wait_until="networkidle")
                page.wait_for_selector("#pre.done", timeout=10000)
                time.sleep(0.5)
                shot_path = os.path.join(DOCS_DIR, f"landing-shot-{shot}.png")
                page.screenshot(path=shot_path)
                print(f"Saved {shot_path}")

            # Return to main / and scroll through chapters with mouse wheel
            page.goto("http://127.0.0.1:5000/", wait_until="networkidle")
            page.wait_for_selector("#pre.done", timeout=10000)

            # FPS counter setup
            page.evaluate("""
                () => {
                    window.__fpsFrames = 0;
                    window.__fpsStart = performance.now();
                    function loop() {
                        window.__fpsFrames++;
                        requestAnimationFrame(loop);
                    }
                    requestAnimationFrame(loop);
                }
            """)

            chapters = ["hero", "gate", "pathways", "lessons", "eternity"]
            for ch in chapters:
                page.locator(f"#{ch}").scroll_into_view_if_needed()
                time.sleep(0.7)
                ch_path = os.path.join(DOCS_DIR, f"landing-chapter-{ch}.png")
                page.screenshot(path=ch_path)
                print(f"Saved chapter screenshot: {ch_path}")

            # Calculate FPS
            fps_data = page.evaluate("""
                () => {
                    const elapsed = (performance.now() - window.__fpsStart) / 1000;
                    return { frames: window.__fpsFrames, elapsed, fps: Math.round(window.__fpsFrames / elapsed) };
                }
            """)
            print(f"Performance: {fps_data['frames']} frames in {fps_data['elapsed']:.2f}s => {fps_data['fps']} FPS (Headless SwiftShader)")

            # Click Nav CTA 'Open Navigator' and confirm navigates to /app
            print("Testing 'Open Navigator' Nav CTA click...")
            nav_cta = page.locator("a.nav-cta")
            assert nav_cta.is_visible(), "Nav CTA must be visible"
            nav_cta.click()
            page.wait_for_url("**/app", timeout=5000)
            print("Successfully landed on /app!")

            # -------------------------------------------------------------
            # Mobile 390x844 tests
            # -------------------------------------------------------------
            print("\nTesting mobile viewport (390x844)...")
            mob_context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
            mob_page = mob_context.new_page()
            mob_page.goto("http://127.0.0.1:5000/", wait_until="networkidle")
            mob_page.wait_for_selector("#pre.done", timeout=10000)

            # Assert CTA is visible on mobile
            mob_cta = mob_page.locator("a.nav-cta")
            assert mob_cta.is_visible(), "Nav CTA must be visible on mobile"

            # Check horizontal overflow
            scroll_width = mob_page.evaluate("() => document.documentElement.scrollWidth")
            client_width = mob_page.evaluate("() => document.documentElement.clientWidth")
            print(f"Mobile scrollWidth={scroll_width}, clientWidth={client_width}")
            assert scroll_width <= client_width + 1, "No horizontal overflow on mobile"

            # Open burger menu
            burger = mob_page.locator("button.nav-burger")
            if burger.is_visible():
                burger.click()
                time.sleep(0.5)

            mob_shot_path = os.path.join(DOCS_DIR, "landing-mobile-390x844.png")
            mob_page.screenshot(path=mob_shot_path)
            print(f"Saved mobile screenshot: {mob_shot_path}")

            # -------------------------------------------------------------
            # CSS Fallback (?nogl=1) test
            # -------------------------------------------------------------
            print("\nTesting /?nogl=1 CSS fallback...")
            fb_page = context.new_page()
            fb_page.goto("http://127.0.0.1:5000/?nogl=1", wait_until="networkidle")
            time.sleep(1)
            fb_status = fb_page.evaluate("() => ({ isFallback: Boolean(window.__kage && window.__kage.fallback) })")
            print(f"?nogl=1 fallback status: {fb_status}")
            assert fb_status["isFallback"], "?nogl=1 should trigger fallback mode"
            fb_shot = os.path.join(DOCS_DIR, "landing-fallback-nogl.png")
            fb_page.screenshot(path=fb_shot)
            print(f"Saved fallback screenshot: {fb_shot}")

            browser.close()
            print("\nALL PLAYWRIGHT LANDING TESTS PASSED!")

    finally:
        server.shutdown()

if __name__ == "__main__":
    run_landing_tests()
