with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

def print_js_snippet(term, length=400):
    pos = text.find(term)
    if pos != -1:
        print(f"\n===== JS SNIPPET FOR '{term}' =====")
        print(text[pos:pos+length])

print_js_snippet("buildWordmark")
print_js_snippet("const word = 'KAGE'")
print_js_snippet("wireNav")
