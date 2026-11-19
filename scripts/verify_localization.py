import re

with open("static/landing/index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open("static/landing/secret-pathways-assets/fonts.css", "r", encoding="utf-8") as f:
    css = f.read()

def find_urls(text):
    return [m for m in re.findall(r'https?://[^\s"\'\)]+', text) if not m.startswith('http://localhost')]

print("Remaining external URLs in index.html:", find_urls(html))
print("Remaining external URLs in fonts.css:", find_urls(css))
