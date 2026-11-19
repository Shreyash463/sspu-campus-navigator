with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

# Find sections by id
sections = ["hero", "gate", "pathways", "lessons", "eternity", "colophon"]
for s in sections:
    pos = text.find(f'id="{s}"')
    if pos != -1:
        print(f"\n--- Section id={s} (offset {pos}) ---")
        print(text[pos:pos+600])
    else:
        print(f"Section {s} NOT found by id")
