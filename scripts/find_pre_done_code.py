with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

# Search for preloader logic and 'done'
pos = 0
while True:
    p = text.find('.done', pos)
    if p == -1:
        break
    print(f"Match at {p}:")
    print(text[max(0, p-60):min(len(text), p+140)])
    print("-" * 40)
    pos = p + 5
