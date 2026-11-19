with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

pos = text.find('shot')
while pos != -1:
    print(text[max(0, pos-40):min(len(text), pos+160)])
    print("=" * 40)
    pos = text.find('shot', pos+4)
