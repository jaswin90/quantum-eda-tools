PY ?= python3

.PHONY: all figures html foundations clean

all: figures html foundations

figures:
	$(PY) scripts/make_figures.py
	$(PY) scripts/make_foundation_figures.py

html:
	$(PY) scripts/build.py

foundations:
	$(PY) scripts/build_foundations.py

clean:
	rm -f docs/index.html docs/figures/*.svg
	rm -rf docs/foundations
