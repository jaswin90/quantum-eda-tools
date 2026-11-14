#!/usr/bin/env python3
"""Assemble the review article into docs/index.html.

Source:   review/template.html, review/sections/*.html, references/references.bib
Output:   docs/index.html (static; maths rendered client-side by vendored KaTeX)

Markup conventions used in the section files
  [@key] or [@a; @b]            citation, numbered in order of first use
  <section id="sec-x"><h2>      numbered section; <h3 id="..."> numbered subsection
  <section data-appendix>       lettered appendix (A, B, ...)
  <section class="unnumbered">  no number (abstract, reading guide)
  <div class="eq" id="eq-x">$$..$$</div>   numbered display equation
  <figure id="fig-x">           numbered figure;  <figure class="tbl" id="tab-x"> table
  @sec:x  @fig:x  @tab:x  @eq:x cross-references

Standard library only:  python3 scripts/build.py
"""
from __future__ import annotations

import datetime as _dt
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = ROOT / "review" / "sections"
TEMPLATE = ROOT / "review" / "template.html"
BIB = ROOT / "references" / "references.bib"
OUT = ROOT / "docs" / "index.html"


# ---------------------------------------------------------------- BibTeX
def parse_bib(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    i = 0
    while True:
        m = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,").search(text, i)
        if not m:
            break
        etype, key = m.group(1).lower(), m.group(2)
        j, depth = m.end(), 1
        while depth and j < len(text):
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        body = text[m.end(): j - 1]
        fields = {"_type": etype}
        k = 0
        fm = re.compile(r"(\w+)\s*=\s*")
        while True:
            f = fm.search(body, k)
            if not f:
                break
            name, p = f.group(1).lower(), f.end()
            if p < len(body) and body[p] == "{":
                d, q = 1, p + 1
                while d and q < len(body):
                    d += {"{": 1, "}": -1}.get(body[q], 0)
                    q += 1
                val = body[p + 1: q - 1]
            else:
                q = body.find(",", p)
                q = len(body) if q < 0 else q
                val = body[p:q].strip()
            fields[name] = val
            k = q
        if key in entries:
            sys.exit(f"duplicate bib key {key}")
        entries[key] = fields
        i = j
    return entries


ACCENTS = {r'{\"u}': "ü", r'{\"a}': "ä", r'{\"o}': "ö", r"{\'o}": "ó", r"{\'e}": "é",
           r"{\'c}": "ć", r"{\aa}": "å", r"{\o}": "ø", r"\&": "&", r"\$": "$"}


def detex(s: str) -> str:
    for a, b in ACCENTS.items():
        s = s.replace(a, b)
    return re.sub(r"[{}]", "", s).replace("--", "–").strip()


def fmt_authors(raw: str) -> str:
    raw = detex(raw)
    parts = [a.strip() for a in raw.split(" and ")]
    etal = any(p.lower() == "others" for p in parts)
    parts = [p for p in parts if p.lower() != "others"]
    names = []
    for p in parts:
        if "," in p:
            last, first = [x.strip() for x in p.split(",", 1)]
            names.append(f"{first} {last}")
        else:
            names.append(p)
    if len(names) > 4:
        names, etal = names[:3], True
    s = ", ".join(names)
    return s + (" et al." if etal else "")


def fmt_entry(e: dict[str, str]) -> str:
    t = e["_type"]
    au = fmt_authors(e.get("author", ""))
    title = html.escape(detex(e.get("title", "")))
    year = e.get("year", "")
    bits = []
    if t == "article":
        venue = html.escape(detex(e.get("journal", "")))
        vol = f" <b>{e['volume']}</b>" if "volume" in e else ""
        pages = f", {html.escape(e['pages'])}" if "pages" in e else ""
        bits = [f"{au}, “{title},” <i>{venue}</i>{vol}{pages} ({year})."]
    elif t in ("book",):
        ed = f", {e['edition']} ed." if "edition" in e else ""
        bits = [f"{au}, <i>{title}</i>{ed} ({html.escape(detex(e.get('publisher', '')))}, {year})."]
    elif t in ("inproceedings", "incollection"):
        bits = [f"{au}, “{title},” in <i>{html.escape(detex(e.get('booktitle', '')))}</i> ({year})."]
    elif t == "techreport":
        bits = [f"{au}, “{title},” {html.escape(detex(e.get('institution', '')))}, "
                f"report {html.escape(e.get('number', ''))} ({year})."]
    else:  # misc
        how = e.get("howpublished", "")
        m = re.match(r"arXiv:(\S+)", how)
        how_html = (f'<a href="https://arxiv.org/abs/{m.group(1)}">arXiv:{m.group(1)}</a>' if m
                    else html.escape(detex(how)))
        bits = [f"{au}, “{title}”" + (f", {how_html}" if how else "") + f" ({year})."]
    if "url" in e:
        u = html.escape(e["url"])
        host = re.sub(r"^https?://(www\.)?", "", e["url"]).split("/")[0]
        bits.append(f' <a class="ref-url" href="{u}">{html.escape(host)}</a>')
    if "verify" in e.get("note", ""):
        bits.append(' <span class="verify" title="bibliographic details to be checked">[verify details]</span>')
    return "".join(bits)


# ---------------------------------------------------------------- assembly
def assemble(body: str, bib: dict[str, dict[str, str]], xref_hook=None) -> dict:
    """Number sections, equations, figures and tables; resolve cross-references and citations.

    Returns the processed body, the table of contents, the reference list and the label map.
    xref_hook(body) -> body runs after local labels are known and before local references are
    resolved, so a caller can rewrite references to other documents first."""
    # -- section numbering -------------------------------------------------
    labels: dict[str, str] = {}
    toc: list[tuple[int, str, str, str]] = []
    out, n2, n3, app = [], 0, 0, 0
    pos = 0
    sec_re = re.compile(r'<section([^>]*)id="([^"]+)"([^>]*)>\s*<h2>(.*?)</h2>', re.S)
    h3_re = re.compile(r'<h3 id="([^"]+)">(.*?)</h3>', re.S)
    for m in sec_re.finditer(body):
        attrs = m.group(1) + m.group(3)
        sid, title = m.group(2), m.group(4)
        if "unnumbered" in attrs:
            num = ""
        elif "data-appendix" in attrs:
            num = chr(ord("A") + app)
            app += 1
        else:
            n2 += 1
            num = str(n2)
        labels[sid] = ("Appendix " + num) if "data-appendix" in attrs else (f"§{num}" if num else title)
        toc.append((2, sid, num, title))
        n3 = 0
        start, end = m.end(), body.find("</section>", m.end())
        seg = body[start:end]

        def h3(mm, num=num):
            nonlocal n3
            n3 += 1
            sub = f"{num}.{n3}" if num else ""
            labels[mm.group(1)] = f"§{sub}"
            toc.append((3, mm.group(1), sub, mm.group(2)))
            pre = f'<span class="secnum">{sub}</span> ' if sub else ""
            return f'<h3 id="{mm.group(1)}">{pre}{mm.group(2)}</h3>'

        seg = h3_re.sub(h3, seg)
        pre = f'<span class="secnum">{num}</span> ' if num else ""
        out.append(body[pos:m.start()])
        out.append(f'<section{m.group(1)}id="{sid}"{m.group(3)}><h2>{pre}{title}</h2>{seg}')
        pos = end
    out.append(body[pos:])
    body = "".join(out)

    # -- equations ---------------------------------------------------------
    neq = 0

    def eq(m):
        nonlocal neq
        neq += 1
        labels[m.group(1)] = f"({neq})"
        inner = m.group(2).rstrip()
        assert inner.endswith("$$"), m.group(1)
        return f'<div class="eq" id="{m.group(1)}">{inner[:-2]} \\tag{{{neq}}}$$</div>'

    body = re.sub(r'<div class="eq" id="([^"]+)">(.*?)</div>', eq, body, flags=re.S)

    # -- figures and tables -----------------------------------------------
    nf = nt = 0

    def fig(m):
        nonlocal nf, nt
        is_tab = "tbl" in m.group(1)
        fid = m.group(2)
        if is_tab:
            nt += 1
            labels[fid] = f"Table {nt}"
        else:
            nf += 1
            labels[fid] = f"Figure {nf}"
        cap = m.group(3).replace("<figcaption>", f"<figcaption><b>{labels[fid]}.</b> ", 1)
        return f'<figure{m.group(1)}id="{fid}">{cap}</figure>'

    body = re.sub(r'<figure([^>]*)id="([^"]+)">(.*?)</figure>', fig, body, flags=re.S)

    # -- cross-references --------------------------------------------------
    def xref(m):
        key = m.group(1) + "-" + m.group(2)
        if key not in labels:
            sys.exit(f"unresolved reference @{m.group(1)}:{m.group(2)}")
        return f'<a class="xref" href="#{key}">{labels[key]}</a>'

    if xref_hook:
        body = xref_hook(body)
    body = re.sub(r"@(sec|fig|tab|eq):([A-Za-z0-9_-]+)", xref, body)

    # -- citations ---------------------------------------------------------
    order: dict[str, int] = {}

    def cite(m):
        keys = [k.strip().lstrip("@") for k in m.group(1).split(";")]
        nums = []
        for k in keys:
            if k not in bib:
                sys.exit(f"unknown citation key {k}")
            order.setdefault(k, len(order) + 1)
            nums.append((order[k], k))
        nums.sort()
        # compress runs of three or more consecutive numbers
        parts, i = [], 0
        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j + 1][0] == nums[j][0] + 1:
                j += 1
            if j - i >= 2:
                parts.append(f'<a href="#ref-{nums[i][1]}">{nums[i][0]}</a>–'
                             f'<a href="#ref-{nums[j][1]}">{nums[j][0]}</a>')
            else:
                parts.extend(f'<a href="#ref-{k}">{n}</a>' for n, k in nums[i:j + 1])
            i = j + 1
        return f'<span class="cite">[{", ".join(parts)}]</span>'

    body = re.sub(r"\[(@[^\]]+)\]", cite, body)

    refs = "\n".join(
        f'<li id="ref-{k}"><span class="refnum">[{n}]</span> {fmt_entry(bib[k])}</li>'
        for k, n in sorted(order.items(), key=lambda kv: kv[1]))
    unused = sorted(set(bib) - set(order))

    # -- table of contents -------------------------------------------------
    toc_html = []
    for lvl, sid, num, title in toc:
        plain = re.sub(r"<[^>]+>", "", title)
        nm = f'<span class="tocnum">{num}</span>' if num else ""
        toc_html.append(f'<li class="toc{lvl}"><a href="#{sid}">{nm}{plain}</a></li>')

    return {"body": body, "toc": "\n".join(toc_html), "refs": refs, "nrefs": len(order),
            "labels": labels, "unused": unused,
            "counts": dict(sections=n2, appendices=app, equations=neq, figures=nf, tables=nt)}


def main() -> None:
    bib = parse_bib(BIB.read_text())
    body = "\n".join(p.read_text() for p in sorted(SECTIONS.glob("*.html")))
    a = assemble(body, bib)
    body, refs, order, unused = a["body"], a["refs"], range(a["nrefs"]), a["unused"]
    c = a["counts"]; n2, app, neq, nf, nt = c["sections"], c["appendices"], c["equations"], c["figures"], c["tables"]

    page = TEMPLATE.read_text()
    page = page.replace("{{TOC}}", a["toc"])
    page = page.replace("{{BODY}}", body)
    page = page.replace("{{REFERENCES}}", refs)
    page = page.replace("{{NREFS}}", str(len(order)))
    page = page.replace("{{BUILD_DATE}}", _dt.date.today().isoformat())
    OUT.write_text(page)
    words = len(re.sub(r"<[^>]+>|\$\$.*?\$\$|\\\(.*?\\\)", " ", body, flags=re.S).split())
    print(f"wrote {OUT.relative_to(ROOT)}: {n2} sections, {app} appendices, {neq} equations, "
          f"{nf} figures, {nt} tables, {len(order)} references, ~{words} words")
    if unused:
        print("uncited bib entries:", ", ".join(unused))


if __name__ == "__main__":
    main()
