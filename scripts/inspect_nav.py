with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find('id="nav"')
print(text[pos:pos+1000])
