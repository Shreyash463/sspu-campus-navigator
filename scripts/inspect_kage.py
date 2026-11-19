with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

print("Title:", re.findall(r'<title>.*?</title>', text))
print("Preloader:", re.findall(r'class="pre-[^"]*"[^>]*>.*?<', text)[:5])
print("Nav brand:", re.findall(r'class="brand"[^>]*>.*?</a>', text, re.DOTALL))
print("Wordmark const:", re.findall(r"const word\s*=\s*'[^']+'", text))
print("word-fb:", re.findall(r'class="word-fb"[^>]*>.*?</div>', text))
print("Rail names:", re.findall(r"names\s*=\s*\[[^\]]+\]", text))
print("Hero h1:", re.findall(r'<h1[^>]*>.*?</h1>', text, re.DOTALL))
