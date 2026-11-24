import os
from PIL import Image, ImageEnhance, ImageFilter

real_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "img", "campus_real"))
out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "img"))
os.makedirs(out_dir, exist_ok=True)

def enhance_img(im, contrast=1.08, sharpness=1.2, color=1.05):
    res = ImageEnhance.Contrast(im).enhance(contrast)
    res = ImageEnhance.Sharpness(res).enhance(sharpness)
    res = ImageEnhance.Color(res).enhance(color)
    return res

assets = {
    # File in campus_real -> target name in static/img
    "page_08_X7.jpg": ("campus_aerial_map.jpg", 1.15, 1.3, 1.1),
    "page_22_X21.jpg": ("intro_gate.jpg", 1.1, 1.25, 1.05),
    "page_23_X22.jpg": ("intro_admin.jpg", 1.1, 1.25, 1.05),
    "page_27_X26.jpg": ("intro_amphi.jpg", 1.12, 1.25, 1.08),
    "page_33_X32.jpg": ("intro_canteen.jpg", 1.08, 1.2, 1.05),
    "page_31_X30.jpg": ("intro_auditorium.jpg", 1.1, 1.25, 1.05),
    "page_37_X36.jpg": ("intro_promenade.jpg", 1.1, 1.25, 1.05),
    "page_07_X6.jpg": ("intro_hostels.jpg", 1.12, 1.25, 1.08),
}

for src_fn, (dst_fn, c, s, col) in assets.items():
    src_fp = os.path.join(real_dir, src_fn)
    dst_fp = os.path.join(out_dir, dst_fn)
    if os.path.exists(src_fp):
        with Image.open(src_fp) as im:
            enh = enhance_img(im, c, s, col)
            enh.save(dst_fp, quality=95)
            # Also save webp
            webp_fp = os.path.splitext(dst_fp)[0] + ".webp"
            enh.save(webp_fp, "WEBP", quality=90)
            print(f"Generated {dst_fn} & {os.path.basename(webp_fp)} ({enh.size})")

# Specifically for the map background:
# page_08_X7.jpg has size (842, 474). Let's resize/crop to 1000x560 with slight border fade for clean overlay
with Image.open(os.path.join(real_dir, "page_08_X7.jpg")) as im:
    enh = enhance_img(im, 1.18, 1.35, 1.12)
    # Resize smoothly to 1000x563
    map_base = enh.resize((1000, 563), Image.LANCZOS)
    map_base.save(os.path.join(out_dir, "campus_map_base.jpg"), quality=95)
    map_base.save(os.path.join(out_dir, "campus_map_base.webp"), "WEBP", quality=92)
    print("Generated calibrated campus_map_base.jpg & .webp (1000x563)")
