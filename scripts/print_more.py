with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

def print_exact(start_sub, length=1200):
    pos = text.find(start_sub)
    if pos != -1:
        print(f"\n===== FROM '{start_sub}' =====")
        print(text[pos:pos+length])

print_exact('class="cards" id="cards"')
print_exact('class="cur" id="cur"')
print_exact('class="sec-eternity"')
print_exact('class="foot"')
