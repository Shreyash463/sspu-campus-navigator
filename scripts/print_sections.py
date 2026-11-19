with open("static/landing/index.html", "r", encoding="utf-8") as f:
    text = f.read()

import re

def print_section(section_id, max_len=1500):
    start = text.find(f'id="{section_id}"')
    if start != -1:
        # find closing section tag or next section
        end = text.find('</section>', start)
        if end != -1:
            print(f"\n=================== SECTION {section_id} ===================")
            print(text[start:end+10][:max_len])
        else:
            print(f"\n=================== SECTION {section_id} (no </section>) ===================")
            print(text[start:start+max_len])

# Preloader & Nav
p_start = text.find('<div id="pre">')
p_end = text.find('</nav>', p_start)
print("\n=================== PRELOADER & NAV ===================")
print(text[p_start:p_end+6])

print_section("hero")
print_section("gate")
print_section("pathways")
print_section("lessons")
print_section("eternity")
