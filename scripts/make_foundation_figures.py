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


# ============================================================== Book 2: classical physics
def fig_c_avoided():
    p = Plot()
    g = 0.02
    p.set_x(-0.15, 0.15)
    p.set_y(0.85, 1.15)
    p.axes([-0.1, -0.05, 0, 0.05, 0.1], [0.9, 1.0, 1.1], "detuning Δ/ω₂ = (ω₁ − ω₂)/ω₂", "mode frequency / ω₂", fmt, fmt)
    xs = frange(-0.15, 0.15, 400)
    p.line([(d, 1 + d) for d in xs], AXIS, width=1.5, dash="6 5")
    p.line([(d, 1.0) for d in xs], AXIS, width=1.5, dash="6 5")
    up = [(d, 1 + d / 2 + 0.5 * math.sqrt(d * d + 4 * g * g)) for d in xs]
    lo = [(d, 1 + d / 2 - 0.5 * math.sqrt(d * d + 4 * g * g)) for d in xs]
    p.line(up, C1)
    p.line(lo, C2)
    p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(1 + g):.1f}" x2="{p.X(0):.1f}" y2="{p.Y(1 - g):.1f}" stroke="{INK}" stroke-width="1.5"/>')
    p.label(0, 1.0, "2g", INK, dx=8, dy=5)
    p.label(0.07, 1.11, "ω₊", C1)
    p.label(0.07, 0.985, "ω₋", C2, dy=20)
    save(p, "fig-c-avoided.svg", "Avoided crossing of two coupled modes with minimum splitting 2g.")


def fig_c_notch():
    qe = 2e4
    left = Plot(w=470, h=380, l=70, r=18)
    left.set_x(-60, 60)
    left.set_y(0, 1.05)
    left.axes([-50, -25, 0, 25, 50], [0, 0.5, 1], "detuning (ω − ω₀)/ω₀ × 10⁶", "|S₂₁|", fmt, fmt)
    right = Plot(w=420, h=380, l=70, r=28)
    right.set_x(0, 1.05)
    right.set_y(-0.52, 0.52)
    right.axes([0, 0.5, 1], [-0.5, 0, 0.5], "Re S₂₁", "Im S₂₁", fmt, fmt)
    for qi, col in ((1e5, C1), (2e4, C2)):
        ql = 1 / (1 / qi + 1 / qe)
        s = [(x, 1 - (ql / qe) / (1 + 2j * ql * x * 1e-6)) for x in frange(-60, 60, 1201)]
        left.line([(x, abs(v)) for x, v in s], col)
        right.line([(v.real, v.imag) for _, v in frange_c(ql, qe)], col)
    left.label(15, 0.25, "Qᵢ = 10⁵", C1, size=13)
    left.label(15, 0.12, "Qᵢ = Qₑ", C2, size=13)
    combine([left, right], "fig-c-notch.svg", "Transmission of a notch-coupled resonator, as magnitude and as a circle in the complex plane.")


def frange_c(ql, qe):
    out = []
    for i in range(2001):
        x = math.tan(math.pi * (i / 2000 - 0.5) * 0.999)   # sweep the whole circle
        out.append((x, 1 - (ql / qe) / (1 + 2j * x)))
    return out


def fig_c_nth():
    p = Plot()
    p.set_x(0.005, 10, log=True)
    p.set_y(1e-8, 1e2, log=True)
    p.axes([0.01, 0.1, 1, 10], [1e-8, 1e-6, 1e-4, 1e-2, 1, 100], "temperature (K)", "mean thermal photon number n̄",
           lambda v: {0.01: "10 mK", 0.1: "100 mK", 1: "1 K", 10: "10 K"}[v],
           lambda v: mf.p10(int(round(math.log10(v)))))
    p.vband(0.01, 0.025, color="#0E8A7A", opacity=0.14)
    p.hline(1e-3)
    h_kb = 4.799e-11
    for f, col, lab in ((1e9, C3, "1 GHz"), (5e9, C1, "5 GHz"), (10e9, C2, "10 GHz")):
        pts = []
        for e in frange(math.log10(0.005), 1, 400):
            T = 10 ** e
            x = f * h_kb / T
            n = 1 / math.expm1(x) if x < 700 else 0
            if n > 1e-8:
                pts.append((T, n))
        p.line(pts, col)
        T0 = {1e9: 0.03, 5e9: 0.09, 10e9: 0.2}[f]
        p.label(T0, 1 / math.expm1(f * h_kb / T0), lab, col, dx=-58, dy=-4)
    save(p, "fig-c-nth.svg", "Thermal photon number versus temperature for 1, 5 and 10 GHz modes.")


# ============================================================== Book 3: quantum mechanics
def hermite(n, x):
    h0, h1 = 1.0, 2 * x
    if n == 0:
        return h0
    for k in range(1, n):
        h0, h1 = h1, 2 * x * h1 - 2 * k * h0
    return h1


def fig_q_qho():
    p = Plot()
    p.set_x(-5, 5)
    p.set_y(0, 5.6)
    p.axes([-4, -2, 0, 2, 4], [0.5, 1.5, 2.5, 3.5, 4.5], "position x / x_zpf", "energy / ħω", fmt, fmt)
    xs = frange(-5, 5, 500)
    # V = (1/2) m w^2 x^2 with x = s * x_zpf:  V/hbar w = s^2 / 4
    p.line([(s, s * s / 4) for s in xs if s * s / 4 <= 5.6], INK2, width=2)
    cols = [C1, C2, C3, C1, C2]
    for n in range(5):
        E = n + 0.5
        p.add(f'<line x1="{p.X(-2*math.sqrt(E)):.1f}" y1="{p.Y(E):.1f}" x2="{p.X(2*math.sqrt(E)):.1f}" y2="{p.Y(E):.1f}" '
              f'stroke="{AXIS}" stroke-width="1" stroke-dasharray="4 4"/>')
        norm = 1 / math.sqrt(2 ** n * math.factorial(n))
        amp = 0.42
        pts = [(s, E + amp * norm * hermite(n, s / math.sqrt(2)) * math.exp(-s * s / 4)) for s in xs]
        p.line(pts, cols[n], width=2)
        p.label(4.1, E, f"n = {n}", cols[n], dy=5, size=13)
    save(p, "fig-q-qho.svg", "Harmonic oscillator potential with its first five levels and wavefunctions.")


def fig_q_rabi():
    p = Plot()
    p.set_x(0, 4)
    p.set_y(0, 1.05)
    p.axes([0, 1, 2, 3, 4], [0, 0.5, 1], "time × Ω_R / 2π", "excited-state probability P₁", fmt, fmt)
    for d, col, lab in ((0, C1, "Δ = 0"), (1, C2, "Δ = Ω_R"), (2, C3, "Δ = 2Ω_R")):
        W = math.sqrt(1 + d * d)
        pts = [(tt, 1 / W ** 2 * math.sin(W * 2 * math.pi * tt / 2) ** 2) for tt in frange(0, 4, 800)]
        p.line(pts, col)
    p.vline(0.5)
    p.label(0.5, 1.0, "π pulse", INK2, dx=6, dy=14, size=13, weight=400)
    p.label(3.15, 0.93, "Δ = 0", C1, size=13)
    p.label(3.15, 0.56, "Δ = Ω_R", C2, size=13)
    p.label(3.15, 0.27, "Δ = 2Ω_R", C3, size=13)
    save(p, "fig-q-rabi.svg", "Rabi oscillations for three detunings.")


def fig_q_decoh():
    T1, Tphi, sig, det = 100.0, 300.0, 2 * math.pi * 5e-3, 2 * math.pi * 0.05   # us, rad/us
    T2 = 1 / (1 / (2 * T1) + 1 / Tphi)
    p = Plot()
    p.set_x(0, 200)
    p.set_y(0, 1.02)
    p.axes([0, 50, 100, 150, 200], [0, 0.5, 1], "delay τ (µs)", "signal", fmt, fmt)
    ts = frange(0, 200, 2000)
    p.line([(t, math.exp(-t / T1)) for t in ts], C2)
    p.line([(t, 0.5 + 0.5 * math.exp(-t / T2 - (sig * t) ** 2 / 2) * math.cos(det * t)) for t in ts], C1, width=1.3)
    p.line([(t, 0.5 + 0.5 * math.exp(-t / T2)) for t in ts], C3, dash="7 4")
    p.label(150, math.exp(-1.5), "T₁ decay", C2, dy=-10, size=13)
    p.label(120, 0.5 + 0.5 * math.exp(-120 / T2), "echo envelope", C3, dy=-10, size=13)
    p.label(8, 0.08, "Ramsey fringes", C1, size=13)
    save(p, "fig-q-decoh.svg", "T1 decay, Ramsey fringes and echo envelope for a qubit.")
    return {"T2_us": round(T2, 1)}


FIGS = [fig_q_qho, fig_q_rabi, fig_q_decoh, fig_m_lorentz, fig_m_yield, fig_c_avoided, fig_c_notch, fig_c_nth]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for f in FIGS:
        r = f()
        if r is not None:
            print(f.__name__, r)
    print("wrote", len(list(OUT.glob("*.svg"))), "figures to", OUT.relative_to(OUT.parents[2]))


if __name__ == "__main__":
    main()
