with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

def print_snippet(title, start_str, end_str):
    print(f"\n==================== {title} ====================")
    p1 = text.find(start_str)
    if p1 == -1:
        print(f"NOT FOUND: {start_str}")
        return
    p2 = text.find(end_str, p1)
    if p2 == -1:
        print(f"END NOT FOUND: {end_str}")
        return
    print(text[p1:p2 + len(end_str)])

print_snippet("Head / Title", "<title>", "</head>")
print_snippet("Preloader & Nav", '<aside id="pre"', '</nav>')
print_snippet("Hero", '<header class="sec sec-hero"', '</header>')
print_snippet("Gate (#gate)", '<section class="sec sec-gate"', '</section>')
print_snippet("Pathways (#pathways)", '<section class="sec sec-pathways"', '</section>')
print_snippet("Lessons (#lessons)", '<section class="sec sec-craft"', '</section>')
print_snippet("Eternity (#eternity)", '<section class="sec sec-eternity"', '</section>')
print_snippet("Footer", '<footer class="foot"', '</footer>')
