with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

# Find non-ascii characters (Japanese characters are in range \u3000-\u9fff)
jp_chars = re.findall(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text)
print(f"Total Japanese characters in index.html: {len(jp_chars)}")

# Find all tags with class jp
jp_tags = re.findall(r'<[^>]*class="[^"]*jp[^"]*"[^>]*>.*?</[^>]+>', text)
print(f"Total tags with class containing jp: {len(jp_tags)}")
for t in jp_tags:
    print("  ", t[:100])
