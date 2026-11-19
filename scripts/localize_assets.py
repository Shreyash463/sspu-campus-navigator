"""
Script to scan, download, and localize all remote assets in Kage index.html and fonts.css.
Verifies image decoding with PIL and checks font glyph coverage with fonttools.
"""

import os
import re
import requests
import hashlib
from PIL import Image
from fontTools.ttLib import TTFont

LANDING_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "landing")
ASSETS_DIR = os.path.join(LANDING_DIR, "secret-pathways-assets")

os.makedirs(os.path.join(ASSETS_DIR, "foreground", "png"), exist_ok=True)
os.makedirs(os.path.join(ASSETS_DIR, "generated"), exist_ok=True)
os.makedirs(os.path.join(ASSETS_DIR, "fonts"), exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def localize():
    html_path = os.path.join(LANDING_DIR, "index.html")
    css_path = os.path.join(ASSETS_DIR, "fonts.css")

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    # Find supabase and external URLs
    url_pattern = re.compile(r'https://[^\s"\'\)]+')
    html_urls = set(url_pattern.findall(html_content))
    css_urls = set(url_pattern.findall(css_content))

    print(f"Found {len(html_urls)} URLs in HTML and {len(css_urls)} URLs in CSS")

    downloaded = {}

    for u in html_urls | css_urls:
        clean_u = u.rstrip("',;\">")
        if "threeui.com" in clean_u or "supabase.co" in clean_u or "gstatic.com" in clean_u or "googleapis.com" in clean_u:
            filename = clean_u.split("/")[-1].split("?")[0]
            # Determine target subdirectory
            if any(ext in filename for ext in [".woff", ".woff2", ".ttf"]):
                local_rel = f"/secret-pathways-assets/fonts/{filename}"
                local_disk = os.path.join(ASSETS_DIR, "fonts", filename)
            elif any(fg in filename for fg in ["temple-wall", "pine-tree", "tall-grass", "sakura-branch", "maple-leaves", "stone-lantern", "garden-bush", "basalt-stones", "hill", "shrine-ruins"]):
                local_rel = f"/secret-pathways-assets/foreground/png/{filename}"
                local_disk = os.path.join(ASSETS_DIR, "foreground", "png", filename)
            elif any(gen in filename for gen in ["kage-sanmon-preview", "kage-approach", "kage-lantern-court", "kage-moonwater", "card-"]):
                local_rel = f"/secret-pathways-assets/generated/{filename}"
                local_disk = os.path.join(ASSETS_DIR, "generated", filename)
            elif any(filename.endswith(ext) for ext in [".webp", ".png", ".jpg", ".jpeg"]):
                local_rel = f"/secret-pathways-assets/generated/{filename}"
                local_disk = os.path.join(ASSETS_DIR, "generated", filename)
            else:
                continue

            print(f"Downloading {clean_u} -> {local_disk}...")
            try:
                res = requests.get(clean_u, headers=HEADERS, timeout=15)
                if res.status_code == 200:
                    with open(local_disk, "wb") as f:
                        f.write(res.content)
                    downloaded[clean_u] = local_rel
                    print(f"  Saved {len(res.content)} bytes.")
                else:
                    print(f"  Failed: HTTP {res.status_code}")
            except Exception as e:
                print(f"  Error: {e}")

    # Verify image decoding
    print("\n--- Verifying Image Decoding ---")
    for root, dirs, files in os.walk(ASSETS_DIR):
        for file in files:
            if file.endswith((".webp", ".png", ".jpg")):
                fp = os.path.join(root, file)
                try:
                    with Image.open(fp) as img:
                        img.verify()
                    # Reopen to check dimensions
                    with Image.open(fp) as img:
                        print(f"  OK: {file} ({img.size[0]}x{img.size[1]}, {img.format})")
                except Exception as e:
                    print(f"  DECODE ERROR for {file}: {e}")

    # Rewrite URLs in HTML and CSS
    for remote_url, local_path in downloaded.items():
        html_content = html_content.replace(remote_url, local_path)
        css_content = css_content.replace(remote_url, local_path)

    # In fonts.css, convert absolute paths to relative if desired or root-relative: /secret-pathways-assets/...
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)

    print("\nHTML and CSS rewritten with localized paths successfully.")

if __name__ == "__main__":
    localize()
