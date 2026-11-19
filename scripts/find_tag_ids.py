with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

for tag_id in ["pre", "top", "hero", "gate", "pathways", "lessons", "eternity"]:
    m = re.search(r'<(\w+)[^>]*id="' + tag_id + r'"[^>]*>', text)
    if m:
        print(f'Tag for id="{tag_id}": {m.group(0)}')
