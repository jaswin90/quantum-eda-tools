#!/usr/bin/env python3
"""Regenerate the reading-order diagram inside curriculum/roadmap.html from curriculum/series.json."""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = json.loads((ROOT / "curriculum" / "series.json").read_text())
W, H, GAP = 140, 58, 158
col = lambda c: 4 + c * GAP
pos = {1: (col(0), 150), 2: (col(1), 58), 3: (col(1), 242), 4: (col(2), 242), 5: (col(3), 58),
       6: (col(3), 242), 7: (col(4), 150), 8: (col(5), 150)}
names = {b["n"]: (f"Book {b['n']}", b["short"], b["slug"] + "/index.html") for b in S["books"]}
names[8] = ("Capstone", "Lab to Foundry", "../index.html")
edges = [(1, 2), (1, 3), (2, 3), (3, 4), (2, 5), (4, 5), (4, 6), (5, 6), (6, 7), (7, 8)]


def anchor(n, side):
    x, y = pos[n]
    return {"r": (x + W, y + H / 2), "l": (x, y + H / 2), "t": (x + W / 2, y), "b": (x + W / 2, y + H)}[side]


parts = []
for a, b in edges:
    (xa, ya), (xb, yb) = pos[a], pos[b]
    if xa == xb:
        (x1, y1), (x2, y2) = anchor(a, "b"), anchor(b, "t")
        d = f"M{x1:.0f},{y1:.0f} L{x2:.0f},{y2 - 7:.0f}"
    else:
        (x1, y1), (x2, y2) = anchor(a, "r"), anchor(b, "l")
        mx = (x1 + x2) / 2
        d = f"M{x1:.0f},{y1:.0f} C{mx:.0f},{y1:.0f} {mx:.0f},{y2:.0f} {x2 - 7:.0f},{y2:.0f}"
    parts.append(f'<path class="edge" d="{d}" marker-end="url(#rm-arrow)"/>')
for n, (x, y) in pos.items():
    k, s, href = names[n]
    cls = "node cap" if n == 8 else "node"
    parts.append(f'<a href="{href}"><g class="{cls}"><rect x="{x}" y="{y}" width="{W}" height="{H}" rx="9"/>'
                 f'<text class="n" x="{x + 11}" y="{y + 22}">{k.upper()}</text>'
                 f'<text x="{x + 11}" y="{y + 42}" style="font-size:12px">{s}</text></g></a>')
svg = ('<svg class="roadmap-svg" viewBox="0 0 940 310" role="img" aria-label="Reading order of the seven books and the capstone review">'
       '<title>Reading order of the series</title><defs><marker id="rm-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" '
       'orient="auto"><path class="arrowhead" d="M0,0 L8,4 L0,8 z"/></marker></defs>' + "".join(parts) + "</svg>")
p = ROOT / "curriculum" / "roadmap.html"
t = p.read_text()
t = re.sub(r'<svg class="roadmap-svg".*?</svg>', lambda m: svg, t, count=1, flags=re.S)
p.write_text(t)
print("updated", p.relative_to(ROOT))
