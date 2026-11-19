"""
Font Glyph Coverage Check for Kage fonts.css.
Inspects character maps (cmap) for all font faces and checks coverage
for required characters: A-Z, a-z, 0-9, +, /, -, ., ,, ', :, &, >, →, ·.
Specifically checks Wordmark face for S, P, U.
Replaces missing faces with our full Onest woff2 fonts if required.
"""

import os
import re
from fontTools.ttLib import TTFont

LANDING_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "landing")
ASSETS_DIR = os.path.join(LANDING_DIR, "secret-pathways-assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
FULL_FONTS_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "fonts")

REQUIRED_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/-.,':&>→·—– ")

def check_fonts():
    css_path = os.path.join(ASSETS_DIR, "fonts.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Parse font faces
    # e.g. font-family: '...'; font-weight: ...; src: url(...)
    blocks = css.split("@font-face")
    results = []

    for idx, b in enumerate(blocks[1:], 1):
        fam_m = re.search(r'font-family:\s*[\'"]?([^\'";]+)[\'"]?', b)
        weight_m = re.search(r'font-weight:\s*(\d+)', b)
        url_m = re.search(r'url\([\'"]?([^\'")]+)[\'"]?\)', b)

        if not (fam_m and url_m):
            continue

        family = fam_m.group(1).strip()
        weight = weight_m.group(1).strip() if weight_m else "400"
        url = url_m.group(1).strip()

        filename = url.split("/")[-1].split("?")[0]
        disk_path = os.path.join(FONTS_DIR, filename)

        if not os.path.exists(disk_path):
            print(f"Font file missing on disk: {disk_path}")
            continue

        font = TTFont(disk_path)
        # Get characters in font cmap
        chars = set()
        for table in font['cmap'].tables:
            for code in table.cmap.keys():
                chars.add(chr(code))

        missing = [c for c in REQUIRED_CHARS if c not in chars]
        has_spu = all(c in chars for c in ["S", "P", "U"])

        print(f"Face #{idx}: family='{family}', weight={weight}, file={filename}")
        print(f"  Total glyphs in cmap: {len(chars)}")
        print(f"  Contains S, P, U: {has_spu}")
        print(f"  Missing required chars count: {len(missing)}")
        if missing:
            print(f"  Sample missing: {missing[:10]}")

        # Check if Wordmark or if missing critical letters
        replaced = False
        if "wordmark" in family.lower() or not has_spu or len(missing) > 10:
            # Check if this face needs replacement
            # "For any face missing glyphs (especially the Wordmark face for the letters S, P, U), replace ONLY that face with the full-Latin Onest woff2 from Google Fonts"
            # Map weight to closest available full onest font: 300, 400, 500, 600, 700
            w = int(weight)
            avail_weights = [300, 400, 500, 600, 700]
            closest_w = min(avail_weights, key=lambda x: abs(x - w))
            full_font_src = os.path.join(FULL_FONTS_DIR, f"onest-{closest_w}.woff2")
            
            if os.path.exists(full_font_src):
                new_filename = f"onest-replaced-{family.lower().replace(' ', '-')}-{weight}.woff2"
                new_disk_path = os.path.join(FONTS_DIR, new_filename)
                with open(full_font_src, "rb") as rf:
                    with open(new_disk_path, "wb") as wf:
                        wf.write(rf.read())
                
                # Update CSS for this block
                new_url = f"/secret-pathways-assets/fonts/{new_filename}"
                css = css.replace(url, new_url)
                replaced = True
                print(f"  --> REPLACED with full Latin Onest weight {closest_w} ({new_filename})")

        results.append({
            "family": family,
            "weight": weight,
            "filename": filename,
            "has_spu": has_spu,
            "missing_count": len(missing),
            "replaced": replaced
        })

    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)

    print("\nSummary of Font Glyph Check:")
    for r in results:
        print(f"  - {r['family']} (wt {r['weight']}): SPU={'YES' if r['has_spu'] else 'NO'}, Missing={r['missing_count']}, Replaced={r['replaced']}")

if __name__ == "__main__":
    check_fonts()
