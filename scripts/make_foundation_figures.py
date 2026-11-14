#!/usr/bin/env python3
"""Generate the SVG figures for the "Foundations of Quantum Engineering" series.

Every curve is computed here from an equation stated in the text. Standard library only:

    python3 scripts/make_foundation_figures.py

Output: docs/foundations/figures/*.svg. Uses the plotting helpers of make_figures.py so the
series and the review share one visual style.
"""
from __future__ import annotations

import cmath
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_figures as mf  # noqa: E402
from make_figures import Plot, C1, C2, C3, INK, INK2, AXIS, SURF, FONT, Phi  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs" / "foundations" / "figures"


def save(plot: Plot, name: str, alt: str) -> None:
    mf.OUT = OUT
    plot.save(name, alt)


def combine(plots: list[Plot], name: str, alt: str) -> None:
    """Place several Plot panels side by side in one SVG."""
    w = sum(p.w for p in plots)
    h = max(p.h for p in plots)
    body, x = [], 0
    for p in plots:
        body.append(f'<g transform="translate({x},0)">' + "\n".join(p.parts) + "</g>")
        x += p.w
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
           f'role="img" aria-label="{alt}" font-family="{FONT}">\n<title>{alt}</title>\n'
           f'<rect width="{w}" height="{h}" fill="{SURF}"/>\n' + "\n".join(body) + "\n</svg>\n")
    (OUT / name).write_text(svg)


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def fmt(v):
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:g}"


# ============================================================== Book 1: mathematics
def fig_m_lorentz():
    left = Plot(w=470, h=380, l=70, r=18)
    left.set_x(0, 10)
    left.set_y(-1.05, 1.05)
    left.axes([0, 2, 4, 6, 8, 10], [-1, 0, 1], "time (periods 2π/ω₀)", "field", fmt, fmt)
    for g, col in ((0.1, C2), (0.01, C1)):          # gamma / omega_0
        pts = [(t, math.exp(-g * math.pi * t) * math.cos(2 * math.pi * t)) for t in frange(0, 10, 1200)]
        left.line(pts, col, width=1.6)
    right = Plot(w=470, h=380, l=70, r=18)
    right.set_x(-0.25, 0.25)
    right.set_y(0, 1.05)
    right.axes([-0.2, -0.1, 0, 0.1, 0.2], [0, 0.5, 1], "detuning (ω − ω₀)/ω₀", "power (normalised)", fmt, fmt)
    for g, col in ((0.1, C2), (0.01, C1)):
        right.line([(d, (g / 2) ** 2 / (d ** 2 + (g / 2) ** 2)) for d in frange(-0.25, 0.25, 1001)], col)
    right.hline(0.5)
    right.label(0.07, 0.85, "γ = 0.1 ω₀", C2, size=13)
    right.label(0.07, 0.75, "γ = 0.01 ω₀", C1, size=13)
    combine([left, right], "fig-m-lorentz.svg",
            "Ring-down of a resonator for two loss rates, and the corresponding Lorentzian spectra.")


def fig_m_yield():
    p = Plot(title="")
    p.set_x(1, 1e4, log=True)
    p.set_y(0, 1.0)
    p.axes([1, 10, 100, 1000, 10000], [0, 0.25, 0.5, 0.75, 1.0], "number of components N",
           "probability all in specification", lambda v: mf.p10(int(round(math.log10(v)))), fmt)
    out = {}
    for k, col in ((2, C2), (3, C1), (4, C3)):
        q = 2 * Phi(k) - 1
        pts = [(10 ** e, q ** (10 ** e)) for e in frange(0, 4, 300)]
        p.line(pts, col)
        out[k] = round(q ** 1000, 3)
    p.label(3.0, 0.40, "Δ/σ = 2", C2)
    p.label(150, 0.55, "Δ/σ = 3", C1)
    p.label(1500, 0.97, "Δ/σ = 4", C3, dy=14)
    save(p, "fig-m-yield.svg", "Probability that all N components are in specification for windows of 2, 3 and 4 sigma.")
    return out


FIGS = [fig_m_lorentz, fig_m_yield]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in FIGS:
        r = f()
        if r is not None:
            print(f.__name__, r)
    print("wrote", len(list(OUT.glob("*.svg"))), "figures to", OUT.relative_to(OUT.parents[2]))


if __name__ == "__main__":
    main()
