with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

def show(label, pattern):
    res = re.findall(pattern, text, re.DOTALL)
    print(f"=== {label} ===")
    for r in res[:3]:
        print(r[:300])
        print("---")

show("Hero chips", r'<div class="chips"[^>]*>.*?</div>\s*</div>')
show("Peek caption", r'<div class="peek-cap"[^>]*>.*?</div>')
show("Chapter 1", r'<section class="sec sec-gate"[^>]*>.*?</section>')
show("Chapter 2 cards", r'<div class="cards-rail".*?</div>\s*</div>\s*</div>')
show("Chapter 3 lessons", r'<section class="sec sec-craft"[^>]*>.*?</section>')
show("Chapter 4 eternity", r'<section class="sec sec-eternity"[^>]*>.*?</section>')
show("Footer", r'<footer class="foot"[^>]*>.*?</footer>')
