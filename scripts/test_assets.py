import urllib.request
import re

try:
    with urllib.request.urlopen("http://127.0.0.1:5000/") as resp:
        html = resp.read().decode("utf-8")
        print("Landing page fetched: HTTP", resp.status, len(html), "bytes")
        
    imgs = re.findall(r'src=["\'](/static/[^"\']+)["\']', html)
    css = re.findall(r'href=["\'](/static/[^"\']+)["\']', html)
    assets = list(set(imgs + css))
    print(f"Checking {len(assets)} local assets on landing...")
    failed = 0
    for a in assets:
        url = f"http://127.0.0.1:5000{a}"
        try:
            with urllib.request.urlopen(url) as r:
                pass
        except Exception as e:
            print(f"FAILED: {a} -> {e}")
            failed += 1
    if failed == 0:
        print("SUCCESS: All landing page assets loaded with 200 OK!")

    with urllib.request.urlopen("http://127.0.0.1:5000/app") as resp:
        app_html = resp.read().decode("utf-8")
        print("App page fetched: HTTP", resp.status, len(app_html), "bytes")

    app_imgs = re.findall(r'href=["\'](/static/img/[^"\']+)["\']', app_html)
    app_scripts = re.findall(r'src=["\'](/static/[^"\']+)["\']', app_html)
    app_css = re.findall(r'href=["\'](/static/css/[^"\']+)["\']', app_html)
    app_assets = list(set(app_imgs + app_scripts + app_css))
    print(f"Checking {len(app_assets)} local assets on app...")
    app_failed = 0
    for a in app_assets:
        url = f"http://127.0.0.1:5000{a}"
        try:
            with urllib.request.urlopen(url) as r:
                pass
        except Exception as e:
            print(f"FAILED app asset: {a} -> {e}")
            app_failed += 1
    if app_failed == 0:
        print("SUCCESS: All app page assets loaded with 200 OK!")
except Exception as e:
    print("Error:", e)
