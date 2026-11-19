"""
Reskins Kage landing page for SSPU Campus Navigator.
Strictly follows Phase 3 instructions:
Text, labels, and links ONLY.
Preserves all Three.js code, shaders, camera rig, cloth simulation, scroll logic, and data-* attributes.
Removes all Japanese characters.
"""

import os
import re

INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "landing", "index.html")

def reskin():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Title & Meta description
    html = re.sub(
        r'<title>.*?</title>',
        '<title>SSPU Campus Navigator — Find every room, lab and path</title>',
        html
    )
    html = re.sub(
        r'<meta name="description" content="[^"]*">',
        '<meta name="description" content="An interactive SSPU campus directory with a live map, search, filters and shortest-route guidance.">',
        html
    )
    html = re.sub(r'<html\s*lang="[^"]*"', '<html lang="en"', html)

    # 2. Preloader
    html = html.replace('Raising the mountain temple', 'Loading the campus')
    html = html.replace('<div class="pre-jp jp">影の道</div>', '<div class="pre-jp jp">SSPU</div>')

    # 3. Nav brand & links
    html = html.replace(
        '<span class="brand-tx"><b>KAGE</b><i>HIDDEN REALMS OF KYOTO</i></span>',
        '<span class="brand-tx"><b>SSPU</b><i>CAMPUS NAVIGATOR</i></span>'
    )
    html = html.replace(
        '<a class="nav-link" href="#gate" data-cursor><span>Temples</span><span class="alt">伽藍</span></a>',
        '<a class="nav-link" href="#gate" data-cursor><span>Campus</span><span class="alt">Start</span></a>'
    )
    html = html.replace(
        '<a class="nav-link" href="#pathways" data-cursor><span>Gardens</span><span class="alt">庭園</span></a>',
        '<a class="nav-link" href="#pathways" data-cursor><span>Explore</span><span class="alt">Map</span></a>'
    )
    html = html.replace(
        '<a class="nav-link" href="#lessons" data-cursor><span>Rituals</span><span class="alt">神事</span></a>',
        '<a class="nav-link" href="#lessons" data-cursor><span>Features</span><span class="alt">Tools</span></a>'
    )
    html = html.replace(
        '<a class="nav-link" href="#eternity" data-cursor><span>Afterlight</span><span class="alt">残光</span></a>',
        '<a class="nav-link" href="#eternity" data-cursor><span>Begin</span><span class="alt">Go</span></a>'
    )

    # Add persistent nav-cta pill button just before burger
    if '<a class="nav-cta"' not in html:
        burger_match = '<button class="nav-burger" aria-label="Menu" data-cursor>'
        nav_cta_btn = '<a class="nav-cta" href="/app" data-cursor>Open Navigator</a>\n  ' + burger_match
        html = html.replace(burger_match, nav_cta_btn)

    # 4. JS Wordmark & rail names & no-WebGL fallback
    html = html.replace("const word = 'KAGE'", "const word = 'SSPU'")
    html = html.replace('<div class="word-fb" aria-hidden="true">KAGE</div>', '<div class="word-fb" aria-hidden="true">SSPU</div>')
    html = html.replace(
        "names = ['The Hidden Gate', 'The Sanmon', 'Still Gardens', 'Sacred Craft', 'Afterlight', 'Colophon']",
        "names = ['Main Gate','Directory','Map','Features','Begin','Colophon']"
    )

    # 5. Hero
    html = html.replace(
        'Chapter 00 — The Hidden Gate',
        'Chapter 00 — The Main Gate'
    )
    html = re.sub(
        r'<h1 class="display h-hero">.*?</h1>',
        '''<h1 class="display h-hero">
      <span class="mask-line"><span>Find every</span></span>
      <span class="mask-line"><span>room, lab and</span></span>
      <span class="mask-line"><span>path on campus.</span></span>
    </h1>''',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p class="hero-sub body" data-rv="up">.*?</p>',
        '<p class="hero-sub body" data-rv="up">Search any lab, hall or office, then follow the shortest route there.</p>',
        html,
        flags=re.DOTALL
    )

    # Four chips (b / p)
    old_chips = re.search(r'<div class="chapters" id="chips">.*?</div>\s*</div>', html, re.DOTALL)
    if old_chips:
        new_chips_html = '''<div class="chapters" id="chips">
      <div class="chip" data-chip="0" data-rv="up" data-cursor><span class="num">01</span>
        <span class="tx"><b>Directory</b><p>Every lab, office and hall in one place.</p></span></div>
      <div class="chip" data-chip="1" data-rv="up" data-cursor><span class="num">02</span>
        <span class="tx"><b>Search</b><p>Find any room in a few keystrokes.</p></span></div>
      <div class="chip" data-chip="2" data-rv="up" data-cursor><span class="num">03</span>
        <span class="tx"><b>Campus Map</b><p>Tap a marker, zoom and pan.</p></span></div>
      <div class="chip" data-chip="3" data-rv="up" data-cursor><span class="num">04</span>
        <span class="tx"><b>Routes</b><p>Shortest path, step by step.</p></span></div>
    </div>'''
        html = html.replace(old_chips.group(0), new_chips_html + '\n  </div>')

    # Hero peek card caption & hero-side
    html = html.replace(
        'aria-label="Preview: Sanmon, before the bell"',
        'aria-label="Preview: the main gate"'
    )
    html = html.replace(
        '<span class="peek-cap"><b class="jp">山門</b><i>Sanmon — before the bell</i></span>',
        '<span class="peek-cap"><b class="jp">GATE</b><i>SSPU — the main gate</i></span>'
    )
    html = html.replace(
        '<span class="v jp">影の道</span>',
        '<span class="v jp">SSPU</span>'
    )

    # 6. Chapter I (#gate)
    html = html.replace(
        '<span class="k"><b>01</b> — The Sanmon</span><span class="rule"></span><span class="k jp">山門</span>',
        '<span class="k"><b>01</b> — The Directory</span><span class="rule"></span><span class="k jp">A–Z</span>'
    )
    html = html.replace(
        'Charred cypress, worn stone, one gate left open.',
        'Every room, lab and office. One place.'
    )
    html = re.sub(
        r'<p class="lead" data-rv="up">.*?</p>',
        '<p class="lead" data-rv="up">Symbiosis Skills and Professional University in Kiwale, Pune, mapped end to end: every department, laboratory, library, office and canteen, with its building, floor, description and opening hours.</p>',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p class="body" data-rv="up">Climb the worn steps.*?</p>',
        '<p class="body" data-rv="up">Search as you type, filter by category or building, then tap a marker on the live map. Details, an open-or-closed status and directions are always one click away.</p>',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<a class="arrowlink" href="#pathways" data-rv="fade" data-cursor>\s*<span>Cross the threshold</span>',
        '<a class="arrowlink" href="/app" data-rv="fade" data-cursor>\n        <span>Open the navigator</span>',
        html
    )
    # Stats (b / span): "30+" Facilities; "A→B" Shortest route; "Live" Open-now status; "Admin" Fully editable.
    old_stats = re.search(r'<div class="gate-stats" data-rv="up">.*?</div>', html, re.DOTALL)
    if old_stats:
        new_stats = '''<div class="gate-stats" data-rv="up">
    <div><b>30+</b><span>Facilities</span></div>
    <div><b>A→B</b><span>Shortest route</span></div>
    <div><b>Live</b><span>Open-now status</span></div>
    <div><b>Admin</b><span>Fully editable</span></div>
  </div>'''
        html = html.replace(old_stats.group(0), new_stats)

    # 7. Chapter II (#pathways)
    html = html.replace(
        '<span class="k"><b>02</b> — Still Gardens</span><span class="rule"></span><span class="k jp">庭園</span>',
        '<span class="k"><b>02</b> — The Map</span><span class="rule"></span><span class="k jp">MAP</span>'
    )
    # Delete three <i class="glow ..."> elements
    html = re.sub(r'<i class="glow[^"]*" style="[^"]*"></i>\s*', '', html)

    # Card labels:
    # Card 1: Directory / 01 / Search and filter + 01 / 03
    html = html.replace(
        '<div class="card-lab"><b>Approach</b><span class="jp">参道</span></div>',
        '<div class="card-lab"><b>Directory</b><span class="jp">01</span></div>'
    )
    html = html.replace(
        '<div class="card-meta"><span>The long climb</span><span>01 / 03</span></div>',
        '<div class="card-meta"><span>Search and filter</span><span>01 / 03</span></div>'
    )
    # Card 2: Map / 02 / Markers and details + 02 / 03
    html = html.replace(
        '<div class="card-lab"><b>Lanterns</b><span class="jp">灯籠</span></div>',
        '<div class="card-lab"><b>Map</b><span class="jp">02</span></div>'
    )
    html = html.replace(
        '<div class="card-meta"><span>Lantern court</span><span>02 / 03</span></div>',
        '<div class="card-meta"><span>Markers and details</span><span>02 / 03</span></div>'
    )
    # Card 3: Routes / 03 / Dijkstra, step by step + 03 / 03
    html = html.replace(
        '<div class="card-lab"><b>Moonwater</b><span class="jp">月影</span></div>',
        '<div class="card-lab"><b>Routes</b><span class="jp">03</span></div>'
    )
    html = html.replace(
        '<div class="card-meta"><span>The reflecting pool</span><span>03 / 03</span></div>',
        '<div class="card-meta"><span>Dijkstra, step by step</span><span>03 / 03</span></div>'
    )

    # 8. Chapter III (#lessons)
    html = html.replace(
        '<span class="k"><b>03</b> — Sacred Craft</span><span class="rule"></span><span class="k jp">手業</span>',
        '<span class="k"><b>03</b> — Features</span><span class="rule"></span><span class="k jp">REQ 1–8</span>'
    )
    html = html.replace(
        'Five chapters. Ninety minutes. One quiet mind.',
        'Eight requirements. One seamless tool.'
    )
    html = re.sub(
        r'<p class="body-lg" data-rv="up">Each chapter is a walk, not a lecture.*?</p>',
        '<p class="body-lg" data-rv="up">Each feature is a step on the way: browse, search, pick on the map, get directions, and keep it all current as an admin.</p>',
        html,
        flags=re.DOTALL
    )

    # 5 .les rows
    old_cur = re.search(r'<div class="cur" id="cur">.*?</div>\s*</div>', html, re.DOTALL)
    if old_cur:
        new_cur = '''<div class="cur" id="cur">
    <div class="les" data-les="0" data-href="/app" data-cursor>
      <span class="k">01</span>
      <h3>Facility directory<em class="jp">REQ 1–2</em></h3>
      <p>Departments, labs, libraries, offices, cafeterias and auditoriums with building, floor and hours.</p>
      <span class="t">Req 1–2</span><i class="bar"></i>
    </div>
    <div class="les" data-les="1" data-href="/app" data-cursor>
      <span class="k">02</span>
      <h3>Search and filter<em class="jp">REQ 3–4</em></h3>
      <p>Instant search plus category and building filters that combine.</p>
      <span class="t">Req 3–4</span><i class="bar"></i>
    </div>
    <div class="les" data-les="2" data-href="/app" data-cursor>
      <span class="k">03</span>
      <h3>Interactive map<em class="jp">REQ 5–6</em></h3>
      <p>Clickable markers, zoom and pan, and a details card with live open status.</p>
      <span class="t">Req 5–6</span><i class="bar"></i>
    </div>
    <div class="les" data-les="3" data-href="/app" data-cursor>
      <span class="k">04</span>
      <h3>Route guidance<em class="jp">REQ 7</em></h3>
      <p>Shortest path over predefined campus paths with step-by-step directions.</p>
      <span class="t">Req 7</span><i class="bar"></i>
    </div>
    <div class="les" data-les="4" data-href="/app" data-cursor>
      <span class="k">05</span>
      <h3>Admin panel<em class="jp">REQ 8</em></h3>
      <p>Add, edit and delete facilities and paths; changes appear instantly.</p>
      <span class="t">Req 8</span><i class="bar"></i>
    </div>
  </div>'''
        html = html.replace(old_cur.group(0), new_cur)

    # 9. Chapter IV (#eternity)
    html = html.replace(
        '<div class="eyebrow" data-rv="fade">Chapter 04 — Afterlight</div>',
        '<div class="eyebrow" data-rv="fade">Chapter 04 — Begin</div>'
    )
    html = html.replace(
        '<h2 class="display" data-rv="up">Afterlight</h2>',
        '<h2 class="display" data-rv="up">Navigate</h2>'
    )
    html = re.sub(
        r'<p class="body-lg" data-rv="up">The gate does not close behind you.*?</p>',
        '<p class="body-lg" data-rv="up">Open the live campus map. No sign-up, no download.</p>',
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<a class="cta" href="#top" data-rv="fade" data-cursor>\s*<i></i><span>Begin the walk</span>',
        '<a class="cta" href="/app" data-rv="fade" data-cursor>\n    <i></i><span>Open the Navigator</span>',
        html
    )

    # 10. Footer
    html = re.sub(
        r'<div class="foot-brand">\s*<svg.*?</svg>\s*<p>.*?</p>\s*</div>',
        '''<div class="foot-brand">
      <svg viewBox="0 0 44 44" fill="none" width="34" height="34" aria-hidden="true">
        <circle cx="22" cy="25" r="8.6" fill="#e0231c" fill-opacity=".9"/>
        <path d="M5 13h34M9 18.4h26M22 8.5v27" stroke="#dfe7e0" stroke-width="1.5"/>
      </svg>
      <p>SSPU Campus Navigator: a searchable directory, live map and route finder for the Kiwale campus.</p>
    </div>''',
        html,
        flags=re.DOTALL
    )

    old_foot_grid = re.search(r'<div><h4>Chapters</h4>.*?</div>\s*<div class="foot-base">', html, re.DOTALL)
    if old_foot_grid:
        new_foot_grid = '''<div><h4>Chapters</h4><ul>
      <li><a href="#gate" data-cursor>Directory</a></li>
      <li><a href="#pathways" data-cursor>Map</a></li>
      <li><a href="#lessons" data-cursor>Features</a></li>
      <li><a href="#eternity" data-cursor>Begin</a></li>
    </ul></div>
    <div><h4>Explore</h4><ul>
      <li><a href="/app" data-cursor>Search a lab</a></li>
      <li><a href="/app" data-cursor>Filter by category</a></li>
      <li><a href="/app" data-cursor>Draw a route</a></li>
      <li><a href="/app" data-cursor>Open now</a></li>
    </ul></div>
    <div><h4>Elsewhere</h4><ul>
      <li><a href="/app" data-cursor>Navigator</a></li>
      <li><a href="/admin" data-cursor>Admin</a></li>
      <li><a href="#top" data-cursor>README</a></li>
    </ul></div>
  </div>
  <div class="foot-base">'''
        html = html.replace(old_foot_grid.group(0), new_foot_grid)

    html = re.sub(
        r'<div class="foot-base">.*?</div>',
        '''<div class="foot-base">
    <span>© 2026 SSPU Campus Navigator</span>
    <span>Symbi Skillympics 2026 · Web Technology</span>
    <span>WebGL · Onest · Pune</span>
  </div>''',
        html,
        flags=re.DOTALL
    )

    # 12. Skip Intro Link & Nav CTA styling
    new_css = '''
/* SSPU Reskin Custom Styling */
.nav-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 14px;
  border: 1px solid var(--vermilion);
  border-radius: 16px;
  color: var(--bone);
  font-family: 'Onest', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-decoration: none;
  background: transparent;
  transition: all 0.25s ease;
  margin-right: 14px;
  white-space: nowrap;
}
.nav-cta:hover {
  background: var(--vermilion);
  color: #ffffff;
}
@media (max-width: 768px) {
  .nav-cta {
    display: inline-flex !important;
    padding: 5px 10px;
    font-size: 10px;
    margin-right: 8px;
  }
}
.skip-intro-link {
  position: fixed;
  bottom: 24px;
  left: 24px;
  z-index: 70;
  font-family: 'Onest', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--bone-dim);
  text-decoration: none;
  padding: 6px 12px;
  background: rgba(5, 7, 10, 0.8);
  border: 1px solid var(--line);
  border-radius: 4px;
  backdrop-filter: blur(8px);
  transition: all 0.25s ease;
}
.skip-intro-link:hover {
  color: var(--bone);
  border-color: var(--vermilion);
  background: rgba(224, 35, 28, 0.12);
}
.les { cursor: pointer; }
'''
    if '.nav-cta {' not in html:
        html = html.replace('</style>', new_css + '\n</style>')

    # Add Skip Intro link before </body>
    if 'skip-intro-link' not in html:
        skip_html = '<a class="skip-intro-link" href="/app" data-cursor>Skip intro &rarr;</a>\n'
        les_click_script = '''
<script>
  document.querySelectorAll('.les').forEach(function(el) {
    el.addEventListener('click', function() {
      window.location.href = '/app';
    });
  });
</script>
'''
        html = html.replace('</body>', skip_html + les_click_script + '</body>')

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print("Reskinning completed successfully.")

if __name__ == "__main__":
    reskin()
