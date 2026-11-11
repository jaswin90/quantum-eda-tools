PY ?= python3

.PHONY: all figures html clean

all: figures html

figures:
	$(PY) scripts/make_figures.py

html:
	$(PY) scripts/build.py

clean:
	rm -f docs/index.html docs/figures/*.svg
