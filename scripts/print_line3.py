with open("static/landing/index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(lines[2][:500])
