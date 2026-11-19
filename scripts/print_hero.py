with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

p1 = text.find('id="hero"')
p2 = text.find('id="gate"')
print(text[p1:p2])
