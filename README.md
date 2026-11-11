# Quantum EDA tools: from laboratory to foundry

A review article, with a research agenda, on design automation for quantum processors. It covers
what the industry is building and buying, the physics and mathematics of each step from qubit
design to calibrated operation, what existing tools do, and seven open problems worth attacking.

**Read it:** open [`docs/index.html`](docs/index.html) in a browser, or enable GitHub Pages
(Settings → Pages → Deploy from branch → `/docs`). The page is self-contained and renders
equations offline with vendored KaTeX.

![Title page and abstract](screenshots/01-title-abstract.png)

## Contents of the review

1. Introduction: the 2024–2026 industrial moment, and the thesis
2. Industrial landscape: modalities, foundries, acquisitions, roadmaps
3. From geometry to Hamiltonian: circuit quantisation, extraction, scaling, inverse design
4. Variability, frequency allocation and yield
5. Materials, interfaces and the coherence budget
6. Packaging, 3D integration and wiring
7. Test, characterisation and calibration
8. Ion traps, photonics, spins, neutral atoms and topological qubits
9. Error correction as the stack-agnostic layer
10. The existing tool landscape and gap map
11. Seven open problems, stated formally
12. Commercial scope, timing and risk
13. Conclusion, plus appendices: figure parameters, glossary, reading guide

About 12,600 words, 39 numbered equations, 7 computed figures, 7 tables and 205 references.

| Equations | Computed figures |
|---|---|
| ![Transmon equations](screenshots/02-transmon-equations.png) | ![Collision yield figure](screenshots/03-collision-yield.png) |
| ![QEC scaling](screenshots/04-qec-scaling.png) | ![Open problem statement](screenshots/05-open-problem.png) |

## Repository layout

```
review/
  template.html          page shell (title block, contents, KaTeX set-up)
  sections/*.html        the article, one file per section, in reading order
references/
  references.bib         every citation (BibTeX; import into Zotero or similar)
  reading-list.md        annotated, tiered reading guide
scripts/
  make_figures.py        computes every figure from the equations in the text
  build.py               numbers sections/equations/figures, resolves citations
docs/                    built site (GitHub Pages root)
  index.html             the assembled article (generated; do not edit)
  assets/css/book.css   book stylesheet (library theme variables)
  assets/js/book.js     dark-mode toggle and library hooks
  figures/*.svg          generated figures
  vendor/katex/          KaTeX 0.16.11 (MIT licence)
screenshots/             previews used in this README
Makefile
```

## Building

Python 3.9+ only, standard library; no packages to install.

```sh
make            # regenerate figures and rebuild docs/index.html
make figures    # figures only
make html       # article only
```

### Writing conventions in `review/sections/`

| Markup | Meaning |
|---|---|
| `[@key]`, `[@a; @b]` | citation, numbered in order of first use from `references.bib` |
| `<section id="sec-x"><h2>` | numbered section (`class="unnumbered"`, `data-appendix` also supported) |
| `<div class="eq" id="eq-x">$$…$$</div>` | numbered display equation |
| `\( … \)` | inline maths (`$` is not a delimiter, so prices like $1.8 bn are safe) |
| `<figure id="fig-x">`, `<figure class="tbl" id="tab-x">` | numbered figure or table |
| `@sec:x`, `@eq:x`, `@fig:x`, `@tab:x` | cross-references |

The build fails on an unknown citation key or an unresolved cross-reference, and lists any
uncited bibliography entries.

## Status and caveats

- Industry information is from public sources to 11 November 2026. Figures marked "reported" are
  press figures, not company disclosures. Intel–Classiq had not closed at the time of writing.
- Bibliography entries tagged `verify` were compiled from memory and need their volume and page
  checked before external use.
- Every figure is computed from a stated model (Appendix A of the review), not digitised from data.
  The collision-yield curve in particular is an illustrative model.
- The byline is set in `review/template.html`.
