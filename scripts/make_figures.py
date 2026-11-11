#!/usr/bin/env python3
"""Generate the SVG figures for the review article.

Every curve is computed from an equation stated in the text; nothing is
digitised from a paper. Standard library only, so the figures can be
regenerated anywhere:

    python3 scripts/make_figures.py

Output: docs/figures/*.svg, plus the key numbers printed to stdout so the
prose can be checked against the plots.
"""
from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "figures"

# Categorical palette, checked with the dataviz validator against #fcfcfb
# (lightness band, chroma floor, CVD separation, contrast): all pass.
C1, C2, C3 = "#1F5FE0", "#B84E14", "#0E8A7A"
INK, INK2, GRID, AXIS, SURF = "#1d222b", "#5b6270", "#e4e2db", "#8a8f98", "#fcfcfb"
FONT = "Inter, 'Helvetica Neue', Arial, sans-serif"


# --------------------------------------------------------------------------
# Minimal SVG plotting
# --------------------------------------------------------------------------
class Plot:
    def __init__(self, w=760, h=460, l=86, r=28, t=34, b=64, title=""):
        self.w, self.h, self.l, self.r, self.t, self.b = w, h, l, r, t, b
        self.parts: list[str] = []
        self.title = title

    # coordinate transforms -------------------------------------------------
    def set_x(self, lo, hi, log=False):
        self.xlo, self.xhi, self.xlog = lo, hi, log

    def set_y(self, lo, hi, log=False):
        self.ylo, self.yhi, self.ylog = lo, hi, log

    def X(self, x):
        a, b = (math.log10(self.xlo), math.log10(self.xhi)) if self.xlog else (self.xlo, self.xhi)
        v = math.log10(x) if self.xlog else x
        return self.l + (v - a) / (b - a) * (self.w - self.l - self.r)

    def Y(self, y):
        a, b = (math.log10(self.ylo), math.log10(self.yhi)) if self.ylog else (self.ylo, self.yhi)
        v = math.log10(y) if self.ylog else y
        return self.h - self.b - (v - a) / (b - a) * (self.h - self.t - self.b)

    # primitives ------------------------------------------------------------
    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=15, fill=INK2, anchor="start", weight=400):
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anchor}" font-weight="{weight}">{s}</text>')

    def axes(self, xticks, yticks, xlabel, ylabel, xfmt=str, yfmt=str):
        x0, x1 = self.l, self.w - self.r
        y0, y1 = self.t, self.h - self.b
        for v in yticks:
            y = self.Y(v)
            self.add(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
            self.text(x0 - 10, y + 5, yfmt(v), anchor="end")
        for v in xticks:
            x = self.X(v)
            self.add(f'<line x1="{x:.1f}" y1="{y1}" x2="{x:.1f}" y2="{y1 + 6}" stroke="{AXIS}" stroke-width="1.5"/>')
            self.text(x, y1 + 26, xfmt(v), anchor="middle")
        self.add(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{AXIS}" stroke-width="1.5"/>')
        self.text((x0 + x1) / 2, self.h - 12, xlabel, anchor="middle", fill=INK)
        self.text(x0 - 4, y0 - 14, ylabel, anchor="start", fill=INK)

    def line(self, pts, color, width=2.5, dash=None):
        d = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<polyline fill="none" stroke="{color}" stroke-width="{width}" '
                 f'stroke-linejoin="round" stroke-linecap="round"{da} points="{d}"/>')

    def hline(self, y, color=AXIS, dash="6 5", width=1.5):
        self.add(f'<line x1="{self.l}" y1="{self.Y(y):.1f}" x2="{self.w - self.r}" y2="{self.Y(y):.1f}" '
                 f'stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')

    def vline(self, x, color=AXIS, dash="6 5", width=1.5):
        self.add(f'<line x1="{self.X(x):.1f}" y1="{self.t}" x2="{self.X(x):.1f}" y2="{self.h - self.b}" '
                 f'stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')

    def band(self, y0, y1, color="#F2A25C", opacity=0.22):
        a, b = sorted((self.Y(y0), self.Y(y1)))
        self.add(f'<rect x="{self.l}" y="{a:.1f}" width="{self.w - self.l - self.r}" height="{b - a:.1f}" '
                 f'fill="{color}" opacity="{opacity}"/>')

    def vband(self, x0, x1, color="#F2A25C", opacity=0.22):
        a, b = sorted((self.X(x0), self.X(x1)))
        self.add(f'<rect x="{a:.1f}" y="{self.t}" width="{b - a:.1f}" height="{self.h - self.t - self.b}" '
                 f'fill="{color}" opacity="{opacity}"/>')

    def dot(self, x, y, color, r=5.5):
        self.add(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{color}" '
                 f'stroke="{SURF}" stroke-width="2"/>')

    def label(self, x, y, s, color=INK, anchor="start", dx=8, dy=-8, size=15, weight=600):
        self.text(self.X(x) + dx, self.Y(y) + dy, s, size=size, fill=color, anchor=anchor, weight=weight)

    def save(self, name, alt):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w}" height="{self.h}" role="img" aria-label="{alt}" '
               f'font-family="{FONT}">\n<title>{alt}</title>\n'
               f'<rect width="{self.w}" height="{self.h}" fill="{SURF}"/>\n'
               + "\n".join(self.parts) + "\n</svg>\n")
        (OUT / name).write_text(svg)


def Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def sup(n):
    return str(n).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))


def p10(e):
    return f"10{sup(e)}"


# --------------------------------------------------------------------------
# Figure: zero-collision yield versus frequency spread
# --------------------------------------------------------------------------
ALPHA, MU = 330.0, 100.0          # |anharmonicity| and designed detuning, MHz
WINDOWS = [(0.0, 17.0), (ALPHA / 2, 4.0), (-ALPHA / 2, 4.0)]  # (centre, half-width), MHz
STRADDLE = ALPHA + 30.0            # outside |Delta| < |alpha| + 30 MHz the CR gate is slow


def p_edge(sigma):
    """Probability that one coupled pair violates a collision condition.

    Delta = f_i - f_j ~ N(MU, 2 sigma^2). Conditions follow the structure of
    Brink et al. (2018) and Hertzberg et al. (2021) with illustrative widths.
    """
    if sigma == 0:
        return 0.0
    s = math.sqrt(2) * sigma

    def P(lo, hi):
        return Phi((hi - MU) / s) - Phi((lo - MU) / s)

    p = sum(P(c - w, c + w) for c, w in WINDOWS)
    p += 1 - P(-STRADDLE, STRADDLE)
    return min(p, 1.0)


def fig_yield():
    chips = [("65 qubits", 72, C1), ("127 qubits", 144, C2), ("1,000 qubits", 1150, C3)]
    pl = Plot()
    pl.set_x(0, 60)
    pl.set_y(0, 1)
    pl.axes([0, 10, 20, 30, 40, 50, 60], [0, 0.25, 0.5, 0.75, 1.0],
            "Junction-induced frequency spread σ<tspan baseline-shift=\"sub\" font-size=\"11\">f</tspan> (MHz)",
            "Probability the chip has no frequency collision",
            yfmt=lambda v: f"{int(v * 100)}%")
    pl.vline(14, color=AXIS)
    pl.text(pl.X(14) + 8, pl.t + 18, "≈ 14 MHz after laser tuning", size=14)
    sig = [i * 0.25 for i in range(0, 241)]
    report = {}
    for name, E, col in chips:
        ys = [(1 - p_edge(s)) ** E for s in sig]
        pl.line(list(zip(sig, ys)), col)
        ly = {72: 0.90, 144: 0.80, 1150: 0.70}[E]
        pl.add(f'<line x1="{pl.X(36):.1f}" y1="{pl.Y(ly):.1f}" x2="{pl.X(40):.1f}" y2="{pl.Y(ly):.1f}" '
               f'stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
        pl.label(40, ly, name, color=col, dx=10, dy=5)
        report[name] = {s: round((1 - p_edge(s)) ** E, 3) for s in (5, 10, 14, 20, 30)}
    pl.save("fig-yield.svg", "Zero-collision yield falls steeply with frequency spread; "
            "larger chips fall earlier.")
    return report


# --------------------------------------------------------------------------
# Figure: frequency shift versus tunnel-barrier thickness change
# --------------------------------------------------------------------------
def fig_junction():
    kappa = 5.1          # nm^-1, barrier height ~1 eV
    f0 = 5000.0          # MHz
    pl = Plot()
    pl.set_x(-0.03, 0.03)
    pl.set_y(-800, 800)
    pl.band(-17, 17)
    pl.axes([-0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03], [-800, -400, 0, 400, 800],
            "Change in average barrier thickness δd (nm)",
            "Qubit frequency shift at 5 GHz (MHz)",
            xfmt=lambda v: f"{v:+.2f}" if v else "0", yfmt=lambda v: f"{v:+d}" if v else "0")
    ds = [i / 1000 for i in range(-30, 31)]
    pl.line([(d, f0 * (math.exp(-kappa * d) - 1)) for d in ds], C1)
    pl.label(-0.03, f0 * (math.exp(kappa * 0.03) - 1), "f ∝ √I<tspan baseline-shift=\"sub\" font-size=\"11\">c</tspan> ∝ exp(−κd)", color=C1, dx=14, dy=26)
    pl.text(pl.X(0.004), pl.Y(17) - 10, "±17 MHz collision window", size=14, fill=INK)
    pl.text(pl.X(0.0) + 0, pl.Y(-650), "0.01 nm ≈ 250 MHz", size=15, fill=INK, anchor="middle", weight=600)
    pl.dot(0.01, f0 * (math.exp(-kappa * 0.01) - 1), C1)
    pl.save("fig-junction.svg", "Qubit frequency depends exponentially on tunnel-barrier thickness: "
            "a hundredth of a nanometre moves a 5 GHz qubit by about 250 MHz.")
    return round(f0 * (1 - math.exp(-kappa * 0.01)), 1)


# --------------------------------------------------------------------------
# Figure: lowest substrate box mode versus chip size
# --------------------------------------------------------------------------
def fig_boxmode():
    c, er = 2.998e8, 11.45
    k = c / math.sqrt(2 * er) / 1e6   # GHz*mm
    pl = Plot()
    pl.set_x(4, 30)
    pl.set_y(0, 16)
    pl.band(4, 8)
    pl.axes([5, 10, 15, 20, 25, 30], [0, 4, 8, 12, 16],
            "Side of a square silicon die, a (mm)", "Lowest TM₁₁ substrate mode (GHz)")
    xs = [4 + i * 0.1 for i in range(0, 261)]
    pl.line([(a, k / a) for a in xs], C1)
    pl.text(pl.X(22), pl.Y(6.4), "Transmon band, 4–8 GHz", size=14, fill=INK)
    for a in (5, 10):
        pl.dot(a, k / a, C1)
    pl.label(5, k / 5, f"5 mm: {k / 5:.1f} GHz", color=INK, dx=12, dy=-6)
    pl.label(10, k / 10, f"10 mm: {k / 10:.1f} GHz", color=INK, dx=12, dy=-10)
    pl.save("fig-boxmode.svg", "The lowest box mode of a silicon die falls into the qubit band "
            "for dies larger than about 8 mm.")
    return round(k, 1)


# --------------------------------------------------------------------------
# Figure: logical error versus code distance, anchored to the Willow memory
# --------------------------------------------------------------------------
PL7 = 1.43e-3    # logical error per cycle at d = 7 (Google Quantum AI, Nature 2025)


def d_needed(lam, target, pl7=PL7):
    d = 7 + 2 * math.log(pl7 / target) / math.log(lam)
    d = math.ceil(d)
    return d if d % 2 else d + 1


def fig_lambda():
    lams = [("Λ = 2.14 (measured)", 2.14, C1), ("Λ = 4", 4.0, C2), ("Λ = 10", 10.0, C3)]
    pl = Plot()
    pl.set_x(3, 45)
    pl.set_y(1e-13, 1e-1, log=True)
    pl.axes([3, 7, 15, 25, 35, 45], [1e-1, 1e-4, 1e-7, 1e-10, 1e-13],
            "Surface-code distance d", "Logical error per QEC cycle",
            yfmt=lambda v: p10(round(math.log10(v))))
    pl.hline(1e-9)
    pl.text(pl.X(30), pl.Y(1e-9) - 8, "target 10⁻⁹", size=14, fill=INK)
    for name, lam, col in lams:
        pts = [(d, PL7 * lam ** (-(d - 7) / 2)) for d in range(3, 46, 2)]
        pts = [(d, y) for d, y in pts if y >= 1e-13]
        pl.line(pts, col)
        dlab, dx, dy, anc = {2.14: (29, 10, -10, "start"), 4.0: (25, 10, -6, "start"),
                             10.0: (13, -12, 6, "end")}[lam]
        pl.label(dlab, PL7 * lam ** (-(dlab - 7) / 2), name, color=col, dx=dx, dy=dy, anchor=anc)
    pl.dot(7, PL7, INK, r=6)
    pl.label(7, PL7, "Willow, d = 7", color=INK, dx=14, dy=-14)
    pl.save("fig-lambda.svg", "Logical error falls exponentially with code distance at a rate set by "
            "the suppression factor Lambda.")
    return {lam: d_needed(lam, 1e-9) for _, lam, _ in lams}


def fig_overhead():
    targets = [("p<tspan baseline-shift=\"sub\" font-size=\"11\">L</tspan> = 10⁻⁶", 1e-6, C1), ("p<tspan baseline-shift=\"sub\" font-size=\"11\">L</tspan> = 10⁻⁹", 1e-9, C2),
               ("p<tspan baseline-shift=\"sub\" font-size=\"11\">L</tspan> = 10⁻¹²", 1e-12, C3)]
    pl = Plot()
    pl.set_x(1.5, 12)
    pl.set_y(10, 1e5, log=True)
    pl.axes([2, 4, 6, 8, 10, 12], [1e1, 1e2, 1e3, 1e4, 1e5],
            "Error-suppression factor Λ", "Physical qubits per logical qubit, 2d² − 1",
            yfmt=lambda v: p10(round(math.log10(v))))
    pl.vline(2.14)
    pl.text(pl.X(2.14) + 8, pl.t + 18, "measured today", size=14)
    out = {}
    for name, t, col in targets:
        lams = [1.5 + i * 0.05 for i in range(0, 211)]
        pts = [(lam, 2 * d_needed(lam, t) ** 2 - 1) for lam in lams]
        pts = [(x, y) for x, y in pts if 10 <= y <= 1e5]
        pl.line(pts, col, width=2.5)
        ly = {1e-6: 3.2e4, 1e-9: 1.9e4, 1e-12: 1.15e4}[t]
        pl.add(f'<line x1="{pl.X(8.6):.1f}" y1="{pl.Y(ly):.1f}" x2="{pl.X(9.2):.1f}" y2="{pl.Y(ly):.1f}" '
               f'stroke="{col}" stroke-width="3" stroke-linecap="round"/>')
        pl.label(9.2, ly, name, color=col, dx=10, dy=5)
        out[name] = {lam: 2 * d_needed(lam, t) ** 2 - 1 for lam in (2.14, 4, 10)}
    pl.save("fig-overhead.svg", "Physical-qubit overhead per logical qubit falls by an order of "
            "magnitude as the suppression factor improves from 2 to 10.")
    return out


# --------------------------------------------------------------------------
# Figure: squeezing after loss
# --------------------------------------------------------------------------
def fig_squeezing():
    pl = Plot()
    pl.set_x(0, 30)
    pl.set_y(0, 16)
    pl.axes([0, 5, 10, 15, 20, 25, 30], [0, 4, 8, 12, 16],
            "Total optical loss from source to detector, 1 − η (%)",
            "Squeezing remaining (dB)")
    pl.hline(10)
    pl.text(pl.X(18), pl.Y(10) - 8, "≈ 10 dB regime targeted by GKP blueprints", size=14, fill=INK)
    out = {}
    for sin, col in ((15, C1), (12, C2)):
        vin = 10 ** (-sin / 10)
        pts = []
        for i in range(0, 301):
            loss = i / 10
            eta = 1 - loss / 100
            v = eta * vin + (1 - eta)
            pts.append((loss, -10 * math.log10(v)))
        pl.line(pts, col)
        pl.label(1.2, pts[12][1], f"{sin} dB source", color=col, dx=4, dy=-10)
        out[sin] = {l: round(-10 * math.log10((1 - l / 100) * vin + l / 100), 2) for l in (3, 7, 10, 20)}
    pl.save("fig-squeezing.svg", "Optical loss caps achievable squeezing regardless of source quality.")
    return out


# --------------------------------------------------------------------------
# Figure: the design-to-fab flow and its feedback loops (diagram)
# --------------------------------------------------------------------------
def fig_flow():
    w, h = 1120, 470
    stages = ["Spec θ*", "Circuit", "Layout x", "Extract θ(x)", "Sign-off",
              "Fabricate", "Warm test", "Cold test", "Calibrate"]
    p = []
    bw, gap, y = 104, 18, 70
    x0 = (w - (len(stages) * bw + (len(stages) - 1) * gap)) / 2
    xs = []
    for i, s in enumerate(stages):
        x = x0 + i * (bw + gap)
        xs.append(x)
        fill = "#eef3fd" if i < 5 else ("#fbefe7" if i < 7 else "#e7f4f2")
        p.append(f'<rect x="{x:.1f}" y="{y}" width="{bw}" height="56" rx="8" fill="{fill}" '
                 f'stroke="{AXIS}" stroke-width="1.2"/>')
        p.append(f'<text x="{x + bw / 2:.1f}" y="{y + 34}" font-size="15" fill="{INK}" '
                 f'text-anchor="middle" font-weight="600">{s}</text>')
        if i:
            ax = x - gap + 2
            p.append(f'<line x1="{ax:.1f}" y1="{y + 28}" x2="{x - 3:.1f}" y2="{y + 28}" stroke="{AXIS}" '
                     f'stroke-width="1.6" marker-end="url(#ah)"/>')
    p.append(f'<text x="{xs[0]:.1f}" y="{y - 22}" font-size="14" fill="{C1}" font-weight="600">DESIGN</text>')
    p.append(f'<text x="{xs[5]:.1f}" y="{y - 22}" font-size="14" fill="{C2}" font-weight="600">BUILD</text>')
    p.append(f'<text x="{xs[7]:.1f}" y="{y - 22}" font-size="14" fill="{C3}" font-weight="600">OPERATE</text>')
    # die record
    ry = 250
    p.append(f'<rect x="{xs[0]:.1f}" y="{ry}" width="{xs[-1] + bw - xs[0]:.1f}" height="64" rx="10" '
             f'fill="{INK}"/>')
    p.append(f'<text x="{w / 2:.1f}" y="{ry + 28}" font-size="17" fill="#f5f3ec" text-anchor="middle" '
             f'font-weight="600">Die record: targets θ*, layout x, extracted θ ± Σθ, process history, '
             f'Rₙ map, cold results, calibrated values</text>')
    p.append(f'<text x="{w / 2:.1f}" y="{ry + 50}" font-size="14" fill="#c8cfdb" text-anchor="middle">'
             f'every stage reads and writes one shared, versioned record</text>')
    for x in xs:
        cx = x + bw / 2
        p.append(f'<line x1="{cx:.1f}" y1="{y + 58}" x2="{cx:.1f}" y2="{ry - 4}" stroke="{AXIS}" '
                 f'stroke-width="1.2" stroke-dasharray="3 4"/>')
    # loops
    loops = [(6, 0, "Loop 1: measured Σₓ → frequency plan and sign-off limits", C2, 360),
             (7, 3, "Loop 2: cold results → recalibrate extraction and loss models", C3, 400),
             (8, 4, "Loop 3: drift and crosstalk in operation → new design rules", C1, 440)]
    for a, b, s, col, yy in loops:
        xa, xb = xs[a] + bw / 2, xs[b] + bw / 2
        p.append(f'<path d="M {xa:.1f} {ry + 66} L {xa:.1f} {yy - 14} L {xb:.1f} {yy - 14} L {xb:.1f} {ry + 70}" '
                 f'fill="none" stroke="{col}" stroke-width="2.2" marker-end="url(#ah{col[1:]})"/>')
        p.append(f'<text x="{(xa + xb) / 2:.1f}" y="{yy + 4}" font-size="14" fill="{col}" '
                 f'text-anchor="middle" font-weight="600">{s}</text>')
    defs = (f'<defs><marker id="ah" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto">'
            f'<path d="M0,0 L9,4.5 L0,9 z" fill="{AXIS}"/></marker>'
            + "".join(f'<marker id="ah{c[1:]}" markerWidth="9" markerHeight="9" refX="7" refY="4.5" '
                      f'orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{c}"/></marker>' for c in (C1, C2, C3))
            + "</defs>")
    alt = ("The nine-stage design-to-fabrication flow, a shared die record beneath it, and three "
           "feedback loops from test and operation back to design.")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
           f'role="img" aria-label="{alt}" font-family="{FONT}"><title>{alt}</title>{defs}'
           f'<rect width="{w}" height="{h}" fill="{SURF}"/>' + "".join(p) + "</svg>\n")
    (OUT / "fig-flow.svg").write_text(svg)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("yield", fig_yield())
    print("junction: 0.01 nm ->", fig_junction(), "MHz")
    print("box mode constant (GHz*mm):", fig_boxmode())
    print("d needed for 1e-9:", fig_lambda())
    print("overhead:", fig_overhead())
    print("squeezing:", fig_squeezing())
    fig_flow()
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
