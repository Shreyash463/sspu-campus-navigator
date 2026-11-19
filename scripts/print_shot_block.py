with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find("const shot = Q.get('shot');")
print(text[pos:pos+600])
