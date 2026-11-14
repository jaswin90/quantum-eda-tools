#!/usr/bin/env python3
"""Assemble the "Foundations of Quantum Engineering" series into docs/foundations/.

Source:   curriculum/series.json            book list, order and prerequisites
          curriculum/template.html          page shell shared by every book
          curriculum/roadmap.html           body of the series roadmap page
          curriculum/<n>-<name>/*.html      chapters of each book, in reading order
          curriculum/references.bib         textbooks and papers cited by the series
          references/references.bib         the review's bibliography (may also be cited)
Output:   docs/foundations/index.html       roadmap
          docs/foundations/<slug>/index.html  one page per book

Markup is the review's (see scripts/build.py) plus references to other documents:
  @b3:sec-x   @b3:eq-x   @b3:fig-x       a label in Book 3 of the series (@b3:sec-x+ adds its title)
  @lf:sec-x   @lf:eq-x                    a label in the review "From Laboratory to Foundry"
and two pedagogical blocks that are counted in the page header:
  <div class="exercises"> ... <details><summary>Solution</summary> ... </details>
  <div class="eda"> ... </div>            "why this matters for quantum EDA" call-out

Standard library only:  python3 scripts/build_foundations.py
"""
from __future__ import annotations

import datetime as _dt
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as review  # noqa: E402  (parse_bib, assemble)

ROOT = Path(__file__).resolve().parent.parent
CUR = ROOT / "curriculum"
OUT = ROOT / "docs" / "foundations"
SERIES = json.loads((CUR / "series.json").read_text())
BOOKS = SERIES["books"]
XREF = re.compile(r"@(b\d|lf):((?:sec|eq|fig|tab)-[A-Za-z0-9_-]+)(\+?)")


def load_bib() -> dict:
    bib = review.parse_bib((ROOT / "references" / "references.bib").read_text())
    own = review.parse_bib((CUR / "references.bib").read_text())
    dup = set(bib) & set(own)
    if dup:
        sys.exit("keys defined in both bibliographies: " + ", ".join(sorted(dup)))
    bib.update(own)
    return bib


MATH = re.compile(r"\$\$.*?\$\$|\\\(.*?\\\)|\\\[.*?\\\]", re.S)


CODE = re.compile(r'<pre class="code"><code>(.*?)</code></pre>', re.S)


def lint(path: Path, text: str) -> None:
    """A '<' inside maths or code starts an HTML tag in the browser; require \\lt or &lt; instead."""
    for m in CODE.finditer(text):
        if "<" in m.group(1):
            line = text.count("\n", 0, m.start()) + 1
            sys.exit(f"{path.relative_to(ROOT)}:{line}: '<' inside a code block; write &lt;")
    for m in MATH.finditer(text):
        if re.search(r"<(?!/?(sub|sup|b|i)>)", m.group(0)):
            line = text.count("\n", 0, m.start()) + 1
            sys.exit(f"{path.relative_to(ROOT)}:{line}: '<' inside maths; write \\lt: {m.group(0)[:70]!r}")


def book_body(b: dict) -> str:
    files = sorted((CUR / b["dir"]).glob("*.html"))
    for p in files:
        lint(p, p.read_text())
    if not files:
        return ('<section id="sec-soon" class="unnumbered"><h2>In preparation</h2>'
                '<p>This book has not been written yet.</p></section>')
    return "\n".join(p.read_text() for p in files)


def written(n: int) -> bool:
    bk = next(x for x in BOOKS if x["n"] == n)
    return any((CUR / bk["dir"]).glob("*.html"))


def pretty(label: str, kind: str) -> str:
    """Turn a local label into the form used when citing it from another document."""
    if kind == "eq":
        return "eq. " + label
    return label


def main() -> None:
    bib = load_bib()
    today = _dt.date.today().isoformat()
    template = (CUR / "template.html").read_text()

    # The review's labels, so the series can point into it.
    rev_body = "\n".join(p.read_text() for p in sorted((ROOT / "review" / "sections").glob("*.html")))
    rev = review.assemble(rev_body, bib)
    labels = {"lf": rev["labels"]}
    titles = {"lf": toc_titles(rev["toc"])}

    # Pass 1: number every book; references to other documents are left in place.
    built = {}
    for b in BOOKS:
        a = review.assemble(book_body(b), bib)
        built[b["n"]] = a
        labels[f"b{b['n']}"] = a["labels"]
        titles[f"b{b['n']}"] = toc_titles(a["toc"])
    road = review.assemble((CUR / "roadmap.html").read_text(), bib)

    def resolve(where: str):
        def sub(m):
            doc, key = m.group(1), m.group(2)
            lab = labels.get(doc, {}).get(key)
            if lab is None:
                if doc.startswith("b") and doc[1:].isdigit() and not written(int(doc[1:])):
                    print(f"warning: {where}: @{doc}:{key} points into an unwritten book")
                    return f"Book {doc[1:]}"
                sys.exit(f"{where}: unresolved reference @{doc}:{key}")
            kind = key.split("-", 1)[0]
            if doc == "lf":
                href, text = f"{up}index.html#{key}", f"Lab to Foundry {pretty(lab, kind)}"
            else:
                n = int(doc[1:])
                bk = next(x for x in BOOKS if x["n"] == n)
                href = f"{up}foundations/{bk['slug']}/index.html#{key}"
                text = f"Book {n} {pretty(lab, kind)}"
            tip = titles.get(doc, {}).get(key)
            if m.group(3) and tip:          # "@b2:sec-x+" also prints the section title
                text += f": {tip}"
            tip = f' title="{html.escape(tip, quote=True)}"' if tip else ""
            return f'<a class="xref ext" href="{href}"{tip}>{text}</a>'
        up = "../../" if where != "roadmap" else "../"
        return sub

    def book_link(n: int, up: str) -> str:
        bk = next(x for x in BOOKS if x["n"] == n)
        return f'<a href="{up}{bk["slug"]}/index.html">Book {n}: {html.escape(bk["short"])}</a>'

    OUT.mkdir(parents=True, exist_ok=True)
    stats = []
    for i, b in enumerate(BOOKS):
        a = built[b["n"]]
        body = XREF.sub(resolve(b["slug"]), a["body"])
        nex = body.count("<summary>Solution")
        c = a["counts"]
        pre = ", ".join(book_link(n, "../") for n in b["prereqs"]) or "school algebra and some calculus"
        header = (
            '<header class="title-block">\n'
            f'  <p class="kicker">{html.escape(SERIES["title"])} · Book {b["n"]} of {len(BOOKS)}</p>\n'
            f'  <h1>{html.escape(b["title"])}</h1>\n'
            f'  <p class="subtitle">{html.escape(b["subtitle"])}</p>\n'
            '  <p class="byline">Jaswin</p>\n'
            f'  <p class="meta">{c["sections"]} chapters · {c["equations"]} numbered equations · '
            f'{nex} exercises with solutions · about {b["hours"]} hours of study</p>\n'
            f'  <p class="meta prereq">Before this book: {pre}. '
            f'<a href="../index.html">Series roadmap</a>.</p>\n'
            '</header>')
        refsec = ""
        if a["nrefs"]:
            refsec = ('<section id="references" class="references">\n  <h2>References and further reading</h2>\n'
                      '  <p class="refnote">Numbered in order of first citation in this book. Entries tagged '
                      '“verify details” were compiled from memory; check volume and page before citing them.</p>\n'
                      f'  <ol class="reflist">\n{a["refs"]}\n  </ol>\n</section>')
        prev_b = BOOKS[i - 1] if i > 0 else None
        next_b = BOOKS[i + 1] if i + 1 < len(BOOKS) else None
        pager = '<nav class="pager" aria-label="Series">'
        pager += (f'<a class="prev" href="../{prev_b["slug"]}/index.html"><span>Previous · Book {prev_b["n"]}</span>'
                  f'{html.escape(prev_b["title"])}</a>' if prev_b else
                  '<a class="prev" href="../index.html"><span>Start</span>Series roadmap</a>')
        pager += (f'<a class="next" href="../{next_b["slug"]}/index.html"><span>Next · Book {next_b["n"]}</span>'
                  f'{html.escape(next_b["title"])}</a>' if next_b else
                  f'<a class="next" href="../../index.html"><span>Capstone</span>'
                  f'{html.escape(SERIES["capstone"]["title"])}</a>')
        pager += "</nav>"
        toc = a["toc"] + ('\n    <li class="toc2"><a href="#references">References</a></li>' if refsec else "")
        page = fill(template, {
            "TITLE": f'{b["title"]} · {SERIES["title"]}',
            "DESCRIPTION": b["blurb"],
            "ROOT": "../../",
            "BRAND": f'Book {b["n"]} · <span>{html.escape(b["short"])}</span>',
            "NAV": ('<a href="../index.html">Roadmap</a><a href="#exercises-index">Exercises</a>'
                    '<a href="../../index.html">Lab to Foundry</a>'),
            "TOC": toc, "HEADER": header, "BODY": body, "REFSECTION": refsec, "PAGER": pager,
            "SERIES": f'{SERIES["title"]}, Book {b["n"]}',
            "SOURCE": f'curriculum/{b["dir"]}/', "BUILD_DATE": today,
        })
        page = page.replace('href="#exercises-index"', 'href="#' + first_exercises(body) + '"')
        d = OUT / b["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page)
        words = len(re.sub(r"<[^>]+>|\$\$.*?\$\$|\\\(.*?\\\)", " ", body, flags=re.S).split())
        stats.append((b["n"], c["sections"], c["equations"], c["figures"], nex, a["nrefs"], words))

    # Roadmap
    cards = []
    for b in BOOKS:
        a = built[b["n"]]
        chs = re.findall(r'<li class="toc2"><a href="#([^"]+)"><span class="tocnum">(\d+)</span>(.*?)</a></li>', a["toc"])
        items = "".join(f'<li><a href="{b["slug"]}/index.html#{sid}">{t}</a></li>' for sid, _, t in chs)
        pre = ", ".join(f"Book {n}" for n in b["prereqs"]) or "none"
        cards.append(
            f'<div class="bookcard" id="book-{b["n"]}">'
            f'<p class="bc-num">Book {b["n"]} · about {b["hours"]} h · needs: {pre}</p>'
            f'<h3 class="bc-title"><a href="{b["slug"]}/index.html">{html.escape(b["title"])}</a></h3>'
            f'<p>{html.escape(b["blurb"])}</p>'
            f'<details><summary>{len(chs)} chapters</summary><ol>{items}</ol></details></div>')
    rbody = XREF.sub(resolve("roadmap"), road["body"]).replace("{{BOOKCARDS}}", "\n".join(cards))
    rbody = rbody.replace("{{TOTALHOURS}}", str(sum(b["hours"] for b in BOOKS)))
    header = ('<header class="title-block">\n'
              '  <p class="kicker">A course in seven books · Roadmap</p>\n'
              f'  <h1>{html.escape(SERIES["title"])}</h1>\n'
              '  <p class="subtitle">From complex numbers to the manufacture of quantum processors: a planned route '
              'into quantum design automation</p>\n'
              '  <p class="byline">Jaswin</p>\n'
              f'  <p class="meta">{len(BOOKS)} books · {sum(s[1] for s in stats)} chapters · '
              f'{sum(s[4] for s in stats)} exercises with solutions · capstone: '
              '<a href="../index.html">From Laboratory to Foundry</a></p>\n</header>')
    refsec = ""
    if road["nrefs"]:
        refsec = ('<section id="references" class="references"><h2>References</h2>'
                  f'<ol class="reflist">{road["refs"]}</ol></section>')
    page = fill(template, {
        "TITLE": f'{SERIES["title"]}: roadmap',
        "DESCRIPTION": SERIES["blurb"], "ROOT": "../", "BRAND": 'Foundations of <span>Quantum Engineering</span>',
        "NAV": '<a href="#sec-order">Reading order</a><a href="#sec-books">Books</a><a href="../index.html">Lab to Foundry</a>',
        "TOC": road["toc"], "HEADER": header, "BODY": rbody, "REFSECTION": refsec,
        "PAGER": ('<nav class="pager" aria-label="Series"><a class="next" href="mathematics/index.html">'
                  f'<span>Begin · Book 1</span>{html.escape(BOOKS[0]["title"])}</a></nav>'),
        "SERIES": SERIES["title"], "SOURCE": "curriculum/", "BUILD_DATE": today,
    })
    (OUT / "index.html").write_text(page)

    print("book  ch  eqs  figs  exercises  refs  words")
    for s in stats:
        print(f"{s[0]:>4} {s[1]:>3} {s[2]:>4} {s[3]:>5} {s[4]:>10} {s[5]:>5} {s[6]:>6}")
    print(f"total words ~{sum(s[6] for s in stats)}; wrote docs/foundations/")


def toc_titles(toc: str) -> dict:
    out = {}
    for sid, title in re.findall(r'<a href="#([^"]+)">(?:<span class="tocnum">[^<]*</span>)?(.*?)</a>', toc):
        out[sid] = re.sub(r"<[^>]+>|\\\(|\\\)", "", title).strip()
    return out


def first_exercises(body: str) -> str:
    m = re.search(r'<div class="exercises" id="([^"]+)"', body)
    return m.group(1) if m else "references"


def fill(t: str, vals: dict) -> str:
    for k, v in vals.items():
        t = t.replace("{{" + k + "}}", str(v))
    left = re.findall(r"\{\{[A-Z_]+\}\}", t)
    if left:
        sys.exit("unfilled template fields: " + ", ".join(left))
    return t


if __name__ == "__main__":
    main()
