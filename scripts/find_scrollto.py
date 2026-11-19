with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

pos = text.find("function scrollTo")
if pos == -1:
    pos = text.find("scrollTo(")
print(text[max(0, pos-40):min(len(text), pos+400)])
