with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

for line in text.splitlines():
    if "__kage" in line:
        print("Line:", line.strip()[:140])
