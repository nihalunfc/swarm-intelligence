# Build the paper: tables from ../results, then the PDF.
#   make            -> main.pdf
#   make arxiv      -> arxiv.tar.gz (sources arXiv accepts: tex, bbl, tables, figures)
#   make clean

LATEX ?= pdflatex -interaction=nonstopmode -halt-on-error
PY ?= python3

main.pdf: main.tex refs.bib make_tables.py $(wildcard ../results/*.md)
	$(PY) make_tables.py
	$(LATEX) main
	bibtex main
	$(LATEX) main
	$(LATEX) main

arxiv: main.pdf
	tar czf arxiv.tar.gz main.tex main.bbl tables figures

clean:
	rm -f main.aux main.bbl main.blg main.log main.out main.pdf arxiv.tar.gz tables/*.tex

.PHONY: arxiv clean
