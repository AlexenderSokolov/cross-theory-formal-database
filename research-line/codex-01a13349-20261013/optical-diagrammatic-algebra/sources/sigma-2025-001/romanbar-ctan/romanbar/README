README for romanbar package, 2025-01-28, v1.0g


TABLE OF CONTENTS
=================

1 Introduction
2 Download
3 Installation
4 Additional Packages
5 Package Compatibility
6 Authors/Maintainer
7 Bug Reports
8 Known Problems


1 INTRODUCTION
==============

This LaTeX package allows to write Roman numbers
(or any other text) with horizontal bars. (Additionally,
commands for converting Arabic numbers into Roman ones
are provided and an \ifnumeric test function.)
The original code for the bars was written by
Prof. Enrico Gregorio (egreg) and published at
https://tex.stackexchange.com/questions/24065/
roman-numerals-formatting/24084#24084

This material is published under the LPPL 1.3c: This work may be
distributed and/or modified under the conditions of the LaTeX Project
Public License, either version 1.3c of this license or (at your option)
any later version. This version of this license is in
https://www.latex-project.org/lppl/lppl-1-3c.txt
and the latest version of this license is in
https://www.latex-project.org/lppl.txt
and version 1.3c or later is part of all distributions of
LaTeX version 2005-12-01 or later.


2 DOWNLOAD
==========

"romanbar" is available on CTAN:
https://www.ctan.org/pkg/romanbar

Also a ZIP file is provided that contains the files:
the manual (romanbar.pdf), the example (romanbar-example.tex),
the compiled example (romanbar-example.pdf),
driver (romanbar.drv), romanbar.dtx,
installation file (romanbar.ins), 
the style file (pagecolor.sty),
and this README, already sorted in a TDS tree:
https://mirrors.ctan.org/install/macros/latex/contrib/romanbar.tds.zip


3 INSTALLATION
==============

Installation with ZIP file in TDS format
----------------------------------------
The ZIP file "romanbar.tds.zip" contains the files
sorted in a TDS tree. Thus you can directly unpack the
ZIP file inside a TDS tree.
See https://www.ctan.org/TDS-guidelines for an explanation
of TDS.
Example:
  cd /...somewhere.../texmf
  unzip /...downloadpath.../romanbar.tds.zip
Do not forget to refresh the file name database of this
TDS tree.
Example:
  texhash /...somewhere.../texmf

Manual installation
-------------------
a) Download the romanbar files from CTAN.
   If necessary, unpack them.
b) Generate the package and driver files:
     tex romanbar.dtx
c) Install the file "*.sty" in your TDS tree:
     cp romanbar.sty TDS:tex/latex/romanbar/
   Replace "TDS:" by the prefix of your TDS tree
   (texmf directory).
d) Create the documentation, if necessary, e.g.
     pdflatex romanbar.dtx
     makeindex -s gind.ist romanbar.idx
     pdflatex romanbar.dtx
     makeindex -s gind.ist romanbar.idx
     pdflatex romanbar.dtx
e) Update the databases if necessary, e.g. for TeXLive
     texhash or mktexlsr.
f) Create the romanbar-example.pdf, if necessary, e.g.
     pdflatex romanbar-example.tex
g) Copy the documentation files to
   "TDS:doc/latex/romanbar/":
   README, romanbar.pdf, romanbar-example.tex,
   romanbar-example.pdf.


4 ADDITIONAL PACKAGES
=====================

romanbar loads the package
trimclip
from the adjustbox package bundle,
https://www.ctan.org/pkg/adjustbox.
The romanbar-example.tex additionally uses
hyperref: http://ctan.org/pkg/hyperref
which again loads other packages
(see the result of the \listfiles command in the log-file
 of the example).


5 PACKAGE COMPATIBILITY
=======================

There are no known incompatibilities.


6 AUTHOR/MAINTAINER
=====================

* Author of the original code for the bars:
   Prof. Enrico Gregorio (egreg), see
   https://tex.stackexchange.com/questions/24065/
    roman-numerals-formatting/24084#24084
* Author of the recent package and current maintainer:
   H.-Martin Münch


7 BUG REPORTS
==============

A bug report should contain:
* Comprehensive problem description. This includes error or
  warning messages.
* \errorcontextlines=\maxdimen can be added in the
  TeX code to get more information in TeX error messages.
* Minimal test file that shows the problem,
  but does not contain any unnecessary packages and code.
* Used drivers/programs.
* Version information about used packages and programs.
* If you are using LaTeX, then add "\listfiles" to the document.
  Then a list of version information is printed at the end
  of the LaTeX run.
* Please no other files than the minimal test file.
  The other files .log, .dvi, .ps, .pdf are seldom
  necessary, so send them only on request.
* Please .zip or .tar.gz your file(s) before sending them!

Bug address
-----------
Bug reports can be send to the maintainer:
  H.-Martin Münch
  <Martin [dot] Muench [at] Uni-Bonn [dot] de>


8 KNOWN PROBLEMS
=================

Depending on used pdf-viewer and zoom level
the bars might not look as good as when printed.
Depending on used printer 
the bars might not look as good as when on screen.