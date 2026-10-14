help:
	@echo "This is the makefile for the mathcommand package"
	@echo "- all: produces mathcommand.pdf mathcommand.sty mathcommand-code.pdf README.md"
	@echo "- clean"
	@echo "- ctan: creates the mathcommand-ctan.zip file tailored for CTAN"

all: mathcommand.sty mathcommand.pdf README.md

mathcommand.sty: mathcommand.dtx mathcommand.ins
	latex mathcommand.ins

README.md: mathcommand.dtx mathcommand.ins
	latex mathcommand.ins

clean:
	rm -f *.aux *.glo *.idx *.aux *.synctex.gz *.out *.toc *.kaux *.diagnose *.log
	rm -f *.bbl *.out *.bbl *.ind *.ilg *.idx
	rm -f mathcommand.sty
	rm -f mathcommand.pdf
	rm -f mathcommand-sources-complete.zip
	rm -f mathcommand-ctan.zip
	rm -f README.md

ctan: mathcommand-ctan.zip

mathcommand.pdf: mathcommand.dtx mathcommand.sty
	pdflatex mathcommand.dtx
	pdflatex mathcommand.dtx
	pdflatex mathcommand.dtx

mathcommand.aux: mathcommand.dtx mathcommand.sty
	pdflatex mathcommand.dtx

sources: clean mathcommand-ctan.zip mathcommand-sources-complete.zip

mathcommand-sources-complete.zip: clean
	\rm -f mathcommand-sources-complete.zip
	cp  mathcommand-sources-complete.zip ../mathcommand-sources-complete-`date +%y-%m-%d_%H:%M`.zip

mathcommand-ctan.zip: mathcommand.pdf mathcommand.sty mathcommand.ins README.md makefile
	rm -f mathcommand-ctan.zip
	rm -rf mathcommand
	mkdir mathcommand
	cp mathcommand.pdf mathcommand/
	cp mathcommand.dtx mathcommand/
	cp makefile mathcommand.ins README.md mathcommand/
	zip mathcommand-ctan.zip mathcommand/*
	rm -rf mathcommand

