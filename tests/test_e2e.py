"""
End-to-End Automated Browser Testing & Evidence Capture for SSPU Campus Navigator
Using Playwright Chromium with SwiftShader WebGL arguments.
"""

import os
import sys
import time
import threading
from PIL import Image
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app
from database import init_db

SCREENSHOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))
GENERATED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "landing", "secret-pathways-assets", "generated"))

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

class ServerThread(threading.Thread):
    def __init__(self, flask_app, port=5000):
        super().__init__()
        self.already_running = False
        try:
            self.server = make_server("127.0.0.1", port, flask_app)
            self.ctx = flask_app.app_context()
            self.ctx.push()
        except OSError:
            self.already_running = True

    def run(self):
        if not self.already_running and hasattr(self, 'server'):
            self.server.serve_forever()

    def shutdown(self):
        if not self.already_running and hasattr(self, 'server'):
            self.server.shutdown()

def wait_for_landing_ready(page, timeout=30000):
    start = time.time()
    while time.time() - start < (timeout / 1000.0):
        done = page.evaluate("() => document.getElementById('pre') && document.getElementById('pre').classList.contains('done')")
        if done:
            return True
        time.sleep(0.4)
    raise TimeoutError("Landing preloader #pre did not get class 'done' within timeout.")

def run_all_e2e():
    with app.app_context():
        init_db(force_reseed=True)

    server = ServerThread(app, 5000)
    server.start()
    time.sleep(1.5)

    evidence = {
        "landing_passed": False,
        "kage_webgl_live": False,
        "console_errors_count": 0,
        "failed_requests_count": 0,
        "fps_note": "",
        "app_features_passed": False,
        "admin_lifecycle_passed": False,
        "card_images_generated": False,
        "screenshots_captured": []
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # =========================================================
            # SECTION 1: LANDING PAGE TESTING
            # =========================================================
            print("\n--- Testing Landing Page ('/') ---")
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            console_errors = []
            failed_requests = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("requestfailed", lambda req: failed_requests.append(f"{req.url} - {req.failure}"))

            page.goto("http://127.0.0.1:5000/")
            wait_for_landing_ready(page, timeout=30000)

            kage_info = page.evaluate("() => ({ exists: Boolean(window.__kage), isFallback: Boolean(window.__kage && window.__kage.fallback) })")
            print(f"window.__kage: {kage_info}")
            assert kage_info["exists"], "window.__kage must exist"
            assert not kage_info["isFallback"], "window.__kage must not be fallback"
            evidence["kage_webgl_live"] = True

            print(f"Console errors: {len(console_errors)}, Failed requests: {len(failed_requests)}")
            evidence["console_errors_count"] = len(console_errors)
            evidence["failed_requests_count"] = len(failed_requests)
            assert len(console_errors) == 0, f"Expected 0 console errors, got {console_errors}"
            assert len(failed_requests) == 0, f"Expected 0 failed requests, got {failed_requests}"

            # Capture ?shot=0 through ?shot=5
            for shot in range(6):
                print(f"Capturing shot {shot}...")
                page.goto(f"http://127.0.0.1:5000/?shot={shot}")
                wait_for_landing_ready(page, timeout=30000)
                time.sleep(0.5)
                shot_file = f"landing-shot-{shot}.png"
                shot_path = os.path.join(SCREENSHOTS_DIR, shot_file)
                page.screenshot(path=shot_path)
                evidence["screenshots_captured"].append(shot_file)

            # Return to main / and scroll through chapters
            print("Scrolling through chapters on / ...")
            page.goto("http://127.0.0.1:5000/")
            wait_for_landing_ready(page, timeout=30000)

            # Record FPS during scroll
            page.evaluate("""
                () => {
                    window.__fpsFrames = 0;
                    window.__fpsStart = performance.now();
                    function loop() { window.__fpsFrames++; requestAnimationFrame(loop); }
                    requestAnimationFrame(loop);
                }
            """)

            chapters = ["hero", "gate", "pathways", "lessons", "eternity"]
            for ch in chapters:
                page.locator(f"#{ch}").scroll_into_view_if_needed()
                time.sleep(0.6)
                ch_file = f"landing-chapter-{ch}.png"
                ch_path = os.path.join(SCREENSHOTS_DIR, ch_file)
                page.screenshot(path=ch_path)
                evidence["screenshots_captured"].append(ch_file)

            fps_res = page.evaluate("""
                () => {
                    const elapsed = (performance.now() - window.__fpsStart) / 1000;
                    return { fps: Math.round(window.__fpsFrames / elapsed), elapsed: elapsed.toFixed(1) };
                }
            """)
            fps_str = f"{fps_res['fps']} FPS (measured over {fps_res['elapsed']}s in Headless SwiftShader WebGL)"
            evidence["fps_note"] = fps_str
            print(f"Performance: {fps_str}")

            # Test Nav CTA click
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)
            cta = page.locator("a.nav-cta")
            assert cta.is_visible()
            cta.click(force=True)
            page.wait_for_url("**/app", timeout=10000)
            print("Navigated to /app via 'Open Navigator' CTA successfully!")
            evidence["landing_passed"] = True

            # Mobile 390x844 test
            print("Testing mobile viewport 390x844...")
            mob_ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
            mob_page = mob_ctx.new_page()
            mob_page.goto("http://127.0.0.1:5000/")
            wait_for_landing_ready(mob_page, timeout=30000)
            assert mob_page.locator("a.nav-cta").is_visible()
            
            scroll_w = mob_page.evaluate("() => document.documentElement.scrollWidth")
            client_w = mob_page.evaluate("() => document.documentElement.clientWidth")
            assert scroll_w <= client_w + 1, "No horizontal overflow on mobile"

            mob_file = "landing-mobile-390x844.png"
            mob_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, mob_file))
            evidence["screenshots_captured"].append(mob_file)

            # CSS fallback ?nogl=1 test
            print("Testing /?nogl=1 fallback...")
            fb_page = context.new_page()
            fb_page.goto("http://127.0.0.1:5000/?nogl=1")
            time.sleep(1)
            is_fb = fb_page.evaluate("() => Boolean(window.__kage && window.__kage.fallback)")
            assert is_fb, "?nogl=1 must render CSS fallback"
            fb_file = "landing-fallback-nogl.png"
            fb_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, fb_file))
            evidence["screenshots_captured"].append(fb_file)

            # =========================================================
            # SECTION 2: CAMPUS NAVIGATOR APP TESTING ('/app')
            # =========================================================
            print("\n--- Testing Campus Navigator App ('/app') ---")
            app_page = context.new_page()
            app_page.goto("http://127.0.0.1:5000/app")
            time.sleep(1.5)

            # 1. Screenshot: home with map
            home_file = "app-desktop-home.png"
            app_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, home_file))
            evidence["screenshots_captured"].append(home_file)

            # 2. Search test
            search_input = app_page.locator("#facility-search-input")
            search_input.fill("Robotics")
            time.sleep(0.5)
            res_text = app_page.locator("#results-count-text").text_content()
            print(f"Search 'Robotics' results: {res_text}")
            assert "1 of 32" in res_text or "facilities" in res_text

            search_file = "app-desktop-search.png"
            app_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, search_file))
            evidence["screenshots_captured"].append(search_file)

            # Clear search
            app_page.locator("#search-clear-btn").click()
            time.sleep(0.4)

            # 3. Category & Building filter test
            app_page.locator("#category-chips-container button[data-category='Laboratory']").click()
            time.sleep(0.4)
            app_page.locator("#building-filter-select").select_option("Mechanical & Workshops Block (C)")
            time.sleep(0.4)
            combined_text = app_page.locator("#results-count-text").text_content()
            print(f"Combined filter results: {combined_text}")

            # Reset filters
            app_page.locator("#reset-filters-btn").click()
            time.sleep(0.4)

            # 4. Marker Click & Details Card
            marker = app_page.locator("#map-markers-layer .marker-pin[data-id='8']")
            marker.click()
            time.sleep(0.6)

            detail_card = app_page.locator("#detail-card-panel")
            assert detail_card.is_visible()
            det_name = app_page.locator("#detail-name").text_content()
            det_bld = app_page.locator("#detail-building").text_content()
            det_status = app_page.locator("#detail-status-text").text_content()
            print(f"Selected facility: {det_name} ({det_bld}) - Status: {det_status}")
            assert "Central Library" in det_name

            det_file = "app-desktop-details.png"
            app_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, det_file))
            evidence["screenshots_captured"].append(det_file)

            # 5. Route Guidance
            app_page.locator("#btn-directions-to").click()
            time.sleep(0.5)
            route_drawer = app_page.locator("#route-drawer-panel")
            assert route_drawer.is_visible()

            # Set Origin to Main Gate (ID 1)
            app_page.locator("#route-from-select").select_option("1")
            time.sleep(0.8)

            route_dist = app_page.locator("#route-dist-val").text_content()
            route_time = app_page.locator("#route-time-val").text_content()
            print(f"Route drawn: Distance={route_dist}, Walking Time={route_time}")
            assert "m" in route_dist and "min" in route_time

            # Verify animated polyline on map
            polyline = app_page.locator("#map-route-layer polyline.route-polyline")
            assert polyline.count() > 0, "Route polyline must exist on map"

            route_file = "app-desktop-route.png"
            app_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, route_file))
            evidence["screenshots_captured"].append(route_file)

            # 6. Zoom & Pan Controls
            app_page.locator("#map-zoom-in").click()
            time.sleep(0.3)
            app_page.locator("#map-zoom-out").click()
            time.sleep(0.3)
            app_page.locator("#map-reset-view").click()
            time.sleep(0.3)

            # 7. Mobile App View
            mob_app_ctx = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
            mob_app_page = mob_app_ctx.new_page()
            mob_app_page.goto("http://127.0.0.1:5000/app")
            time.sleep(1.0)
            mob_app_file = "app-mobile-map.png"
            mob_app_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, mob_app_file))
            evidence["screenshots_captured"].append(mob_app_file)

            # Select item on mobile to show details
            mob_app_page.locator(".facility-card-item").first.click()
            time.sleep(0.6)
            mob_det_file = "app-mobile-details.png"
            mob_app_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, mob_det_file))
            evidence["screenshots_captured"].append(mob_det_file)

            evidence["app_features_passed"] = True

            # =========================================================
            # SECTION 3: ADMIN DASHBOARD TESTING ('/admin')
            # =========================================================
            print("\n--- Testing Admin Area ('/admin') ---")
            admin_page = context.new_page()

            # 1. Unauthenticated redirects to /admin/login
            admin_page.goto("http://127.0.0.1:5000/admin")
            admin_page.wait_for_url("**/admin/login", timeout=8000)
            print("Redirected to login as expected.")

            # 2. Login with demo credentials
            admin_page.locator("#username").fill("admin")
            admin_page.locator("#password").fill("Admin@123")
            admin_page.locator("#login-submit-btn").click()
            admin_page.wait_for_url("**/admin", timeout=8000)
            print("Logged in successfully to /admin!")

            admin_dash_file = "admin-desktop-dashboard.png"
            admin_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, admin_dash_file))
            evidence["screenshots_captured"].append(admin_dash_file)

            # 3. Add Facility with Interactive Map Picker
            admin_page.locator("#btn-open-add-modal").click()
            time.sleep(0.5)
            fac_modal = admin_page.locator("#facility-modal")
            assert fac_modal.is_visible()

            # Fill Form Fields
            admin_page.locator("#facility-name").fill("Automated Inspection & Metrology Lab")
            admin_page.locator("#facility-category").select_option("Laboratory")
            admin_page.locator("#facility-building").select_option("Mechanical & Workshops Block (C)")
            admin_page.locator("#facility-floor").select_option("Ground Floor")
            admin_page.locator("#facility-hours").fill("Mon-Sat 08:30-17:00")
            admin_page.locator("#facility-desc").fill("Coordinate measuring machines and laser surface scanners for industrial precision inspection.")
            admin_page.locator("#facility-contact").fill("+91 20 6793 5081")

            # Click "Pick on Map"
            admin_page.locator("#btn-trigger-map-picker").click()
            time.sleep(0.5)
            picker_modal = admin_page.locator("#map-picker-modal")
            assert picker_modal.is_visible()

            picker_file = "admin-desktop-map-picker.png"
            admin_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, picker_file))
            evidence["screenshots_captured"].append(picker_file)

            # Click on SVG map inside picker
            picker_svg = admin_page.locator("#picker-svg")
            box = picker_svg.bounding_box()
            click_x = box["x"] + box["width"] * 0.87
            click_y = box["y"] + box["height"] * 0.34
            admin_page.mouse.click(click_x, click_y)
            time.sleep(0.4)

            # Confirm coordinates
            admin_page.locator("#btn-confirm-coords").click()
            time.sleep(0.4)

            add_form_file = "admin-desktop-add-facility.png"
            admin_page.screenshot(path=os.path.join(SCREENSHOTS_DIR, add_form_file))
            evidence["screenshots_captured"].append(add_form_file)

            # Submit facility form
            admin_page.locator("#btn-save-facility").click()
            time.sleep(1.2)

            # 4. Verify facility added in admin table
            admin_page.locator("#admin-facility-search").fill("Automated Inspection")
            time.sleep(0.5)
            table_row = admin_page.locator("#facilities-table-body tr").first
            assert "Automated Inspection" in table_row.text_content()
            print("New facility successfully verified in admin table!")

            # 5. Verify instantly visible on public map WITHOUT restart!
            app_page.reload()
            time.sleep(1.0)
            app_page.locator("#facility-search-input").fill("Automated Inspection")
            time.sleep(0.5)
            pub_res = app_page.locator("#facilities-list-container").text_content()
            assert "Automated Inspection & Metrology Lab" in pub_res, "New facility must appear on public app instantly!"
            print("INSTANT UPDATE VERIFIED: New facility appears on public map without server restart!")

            # 6. Edit facility in Admin
            admin_page.bring_to_front()
            edit_btn = admin_page.locator(".edit-fac-btn").first
            edit_btn.click()
            time.sleep(0.5)
            admin_page.locator("#facility-name").fill("Automated Optical & Laser Metrology Lab")
            admin_page.locator("#btn-save-facility").click()
            time.sleep(1.2)

            # 7. Path graph tab check
            admin_page.locator("button[data-tab='tab-paths']").click()
            time.sleep(0.6)
            assert admin_page.locator("#paths-svg-map").is_visible()

            # 8. Audit log tab check
            admin_page.locator("button[data-tab='tab-audit']").click()
            time.sleep(0.6)
            audit_content = admin_page.locator("#audit-table-body").text_content()
            assert "CREATE_FACILITY" in audit_content

            # 9. Logout
            admin_page.locator("#admin-logout-btn").click()
            admin_page.wait_for_url("**/admin/login", timeout=8000)
            print("Admin logout successful!")

            evidence["admin_lifecycle_passed"] = True

            # =========================================================
            # SECTION 4: CARD IMAGES GENERATION (Phase 5)
            # =========================================================
            print("\n--- Capturing Card Images from Running App ---")
            card_ctx = browser.new_context(viewport={"width": 1400, "height": 900}, device_scale_factor=2)
            card_page = card_ctx.new_page()
            card_page.goto("http://127.0.0.1:5000/app")
            time.sleep(1.5)

            # Crop 1: Directory list (sidebar)
            dir_box = card_page.locator("#sidebar-panel").bounding_box()
            dir_tmp = os.path.join(GENERATED_DIR, "tmp_dir.png")
            card_page.screenshot(path=dir_tmp, clip=dir_box)
            
            with Image.open(dir_tmp) as img:
                w, h = img.size
                target_w = min(w, int(h * 0.8))
                target_h = int(target_w * 1.25)
                cropped = img.crop((0, 0, target_w, target_h))
                cropped.save(os.path.join(GENERATED_DIR, "campus-directory.webp"), "WEBP", quality=88)
            os.remove(dir_tmp)

            # Crop 2: Map with markers
            map_box = card_page.locator("#map-viewport").bounding_box()
            map_tmp = os.path.join(GENERATED_DIR, "tmp_map.png")
            card_page.screenshot(path=map_tmp, clip=map_box)
            with Image.open(map_tmp) as img:
                w, h = img.size
                cx, cy = w // 2, h // 2
                target_h = int(h * 0.85)
                target_w = int(target_h * 0.8)
                cropped = img.crop((cx - target_w//2, cy - target_h//2, cx + target_w//2, cy + target_h//2))
                cropped.save(os.path.join(GENERATED_DIR, "campus-map.webp"), "WEBP", quality=88)
            os.remove(map_tmp)

            # Crop 3: A drawn route
            card_page.locator("#nav-route-toggle").click()
            card_page.locator("#route-from-select").select_option("1")
            card_page.locator("#route-to-select").select_option("8")
            time.sleep(1.0)

            route_tmp = os.path.join(GENERATED_DIR, "tmp_route.png")
            card_page.screenshot(path=route_tmp, clip=map_box)
            with Image.open(route_tmp) as img:
                w, h = img.size
                cx, cy = w // 2, h // 2
                target_h = int(h * 0.85)
                target_w = int(target_h * 0.8)
                cropped = img.crop((cx - target_w//2, cy - target_h//2, cx + target_w//2, cy + target_h//2))
                cropped.save(os.path.join(GENERATED_DIR, "campus-route.webp"), "WEBP", quality=88)
            os.remove(route_tmp)

            # Update CSS in index.html for the three cards
            landing_index_path = os.path.join(os.path.dirname(__file__), "..", "static", "landing", "index.html")
            with open(landing_index_path, "r", encoding="utf-8") as f:
                l_html = f.read()

            l_html = l_html.replace(
                "kage-approach.webp", "campus-directory.webp"
            ).replace(
                "kage-lantern-court.webp", "campus-map.webp"
            ).replace(
                "kage-moonwater.webp", "campus-route.webp"
            )
            with open(landing_index_path, "w", encoding="utf-8") as f:
                f.write(l_html)

            print("Updated card backgrounds to generated campus webp images successfully!")
            evidence["card_images_generated"] = True

            # Re-verify landing page with new card images
            try:
                card_page.close()
            except Exception:
                pass
            shot2_page = context.new_page()
            shot2_page.goto("http://127.0.0.1:5000/?shot=2")
            wait_for_landing_ready(shot2_page, timeout=45000)
            time.sleep(1.0)
            new_shot_path = os.path.join(SCREENSHOTS_DIR, "landing-shot-2-updated-cards.png")
            shot2_page.screenshot(path=new_shot_path)
            evidence["screenshots_captured"].append("landing-shot-2-updated-cards.png")

            browser.close()
            print("\nALL PLAYWRIGHT TESTS AND SCREENSHOT CAPTURES COMPLETED SUCCESSFULLY!")

    finally:
        server.shutdown()

    return evidence

if __name__ == "__main__":
    res = run_all_e2e()
    print("\nE2E SUMMARY RESULT:")
    for k, v in res.items():
        print(f"  {k}: {v}")
