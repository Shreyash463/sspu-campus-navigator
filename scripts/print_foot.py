with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

p1 = text.find('<footer class="foot"')
p2 = text.find('</footer>', p1)
print(text[p1:p2+9])
