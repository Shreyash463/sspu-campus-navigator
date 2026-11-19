with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

p1 = text.find('id="lessons"')
p2 = text.find('</section>', p1)
print(text[p1:p2])
