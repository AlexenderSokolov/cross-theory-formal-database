#
# Makefile for aomart package
#
# This file is in public domain
#
# $Id: Makefile,v 1.10 2025/03/06 20:39:10 boris Exp $
#

PACKAGE=aomart

SAMPLES = \
	aomsample.tex\
	aomsample1.tex \
	aomfrench.tex

SCRIPTS = aom-fullref.pl

MAN1 = ${SCRIPTS:%.pl=%.1}


PDF = $(PACKAGE).pdf ${SAMPLES:%.tex=%.pdf}

all:  ${PDF} ${MAN1}

%.1: %.pl
	pod2man -c "LATEX AOMART" -n $* -s 1 -r "" $< > $@


%.pdf:  %.dtx   $(PACKAGE).cls
	pdflatex $<
	- bibtex $*
	pdflatex $<
	- makeindex -s gind.ist -o $*.ind $*.idx
	- makeindex -s gglo.ist -o $*.gls $*.glo
	pdflatex $<
	while ( grep -q '^LaTeX Warning: Label(s) may have changed' $*.log) \
	do pdflatex $<; done


%.cls:   %.ins %.dtx  
	pdflatex $<

%.pdf:  %.tex   $(PACKAGE).cls
	pdflatex $<
	- bibtex $*
	pdflatex $<
	while ( grep -q '^LaTeX Warning: Label(s) may have changed' $*.log) \
	do pdflatex $<; done

aomsample1.tex: aom-fullref.pl aomsample.tex
	perl aom-fullref.pl aomsample.tex > aomsample1.tex


.PRECIOUS:  $(PACKAGE).cfg $(PACKAGE).cls


clean:
	$(RM)  $(PACKAGE).cls *.log *.aux \
	*.cfg *.glo *.idx *.toc \
	*.ilg *.ind *.out *.lof \
	*.lot *.bbl *.blg *.gls \
	*.dvi *.ps *.thm *.tgz *.zip *.rpi *.hd

distclean: clean
	$(RM) $(PDF) aomsample1.tex *.1

#
# Archive for the distribution. Includes typeset documentation
#
archive:  all clean
	COPYFILE_DISABLE=1  \
	tar -C .. -czvf ../$(PACKAGE).tgz --exclude '*~' \
	--exclude '*.tgz' --exclude '*.zip'  --exclude CVS $(PACKAGE)
	mv ../$(PACKAGE).tgz .

zip:  all clean
	${MAKE} $(PACKAGE).cls
	$(RM) *.log
	zip -r  $(PACKAGE).zip * -x '*~' -x '*.tgz' -x '*.zip' -x CVS -x 'CVS/*'
