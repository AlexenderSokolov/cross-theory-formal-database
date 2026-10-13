PAPER=final-theoretics
LATEX=pdflatex
BIBTEX=biber


SRCS=$(wildcard *.tex)
REFS=$(wildcard *.bib)
# FIGS=$(wildcard FIGS/*)

$(PAPER).pdf: $(SRCS) $(REFS) $(FIGS)
	$(LATEX) $(basename $@)
	$(BIBTEX) $(basename $@)
	$(LATEX) $(basename $@)
	$(LATEX) $(basename $@)

clean:
	rm -f *~ *.dvi *.aux *.nav *.snm *.toc *.bbl *.log *.blg *.out $(PAPER).ps $(PAPER).pdf *.synctex.gz *.fls *.fdb_latexmk *.bcf *.run.xml
