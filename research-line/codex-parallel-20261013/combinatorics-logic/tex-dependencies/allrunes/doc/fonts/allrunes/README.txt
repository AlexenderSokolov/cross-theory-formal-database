ALLRUNES
  The allrunes package is a set of fonts and a LaTeX package
  for writing runes of all kinds using LaTeX.

AUTHOR AND HOMEPAGE
  Carl-Gustav Werner is the author of allrunes.
  More information can be found at
  http://www.maths.lth.se/~carl/allrunes/

COPYRIGHT
  This program is provided under the terms of the
  LaTeX Project Public License distributed from CTAN
  archives in the directory macros/latex/base/lppl.txt.
  (C) 2001-2014 Carl-Gustav Werner

VERSION
  This README.txt describes the allrunes version 2.1

CHANGES
  1.0   First public release.
  1.0.1 Removed a few remaining 8-bit characters from
        frum.mf. They didn't work with the new MiKTeX
        package handling system. Also added a lost table,
        added an example and corrected a few spelling
        mistakes in the documentation.
  2.0   Added type1 versions for the main types of the
        allrunes fonts, and support for them in the LaTeX package.
        Merged the former Scandinavian-Gothic and the Continental
        font families to a Common Germanic font family. Renamed the
        commands for flipping and turning runes. Made the commands
        for flipping and turning runes work for all six font families.
        Inserted kerning information for the Common Germanic and
        Anglo-Frisian font families. Complemented the sets of runes
        with a few more, especially the Medieval one. Corrected many
        spelling mistakes in the documentation.
  2.1   Modified the handling of type1 fontes to take advantage
        of the new map-file handling system of MiKTeX- and teTeX-
        implementations. Removed a bug that prevented the use of
        medieval rune with straight twigs. Minor updates to the
        documentation.
  2.1.1 Bugfix. \S and \P didn't work in ordinary text.
        Updated the installation instructions in this file.
        

FILES AND DIRECTORIES AT CTAN
  README.txt     This file.
  allrunes.dtx   The source for the allrunes Metafont fonts and
                 LaTeX package.
  allrunes.ins   Driver file for allrunes.dtx
  allrunes.ps    PostScript version of the documentation,
                 using only mf (pk) fonts.
  allrunes.pdf   Pdf version of the documentation,
                 using only type1 fonts.
  type1          Directory for the type1 fonts, containing:
    pfb          Directory for the pfb files
    allrunes.map Map file for mapping the type1 file names

REQUIREMENTS
  The installation of the allrunes package requires the docstrip
  package. Using the allrunes package requires the ifthen package.
  Processing the documentation for the allrunes package requires
  the fontenc package and the ec fonts. I do not know what version
  of LaTeX is required.

INSTALLATION (OF THE LATEX PACKAGE AND THE METAFONT SOURCE FILES)
  The installation procedure is described in the documentation, but
  since there is weak catch 22, in that you might need the fonts to
  produce the documentation, and you might need the documentation to
  install the fonts, it's also described here. The descriptions below
  are intended to be correct for MiKTeX version 2.9, and for
  texlive version 2012 in ubuntu.

  1. Download the files allrunes.ins and allrunes.dtx to a preferably
     empty directory. If you intend to keep the documentation, you'd
     better create a suitable directory and put the files there right
     now; like
       <tex doc base>/fonts/allrunes/
     In a typical MiKTeX system it would be
       C:\Local TeX Files\doc\fonts\allrunes\
     (See "Integrating Local Additions" in the MiKTeX-documentation.)
     In a texlive system it might be like
       /usr/local/share/texmf/doc/fonts/allrunes/
  2. Start a window where you can enter commands from the keyboard,
     i.e. get an DOS prompt on a Windows machine or a xterm-window
     on a UNIX/linux machine. It might be necessery to run as Administrator
     in Windows or as root (or using sudo) in UNIX/linux. Keep this window
     open, you will need it throughout the entire installation.
  3. Go to the directory where you did put the files allrunes.dtx
     and allrunes.ins
  4. Run the command
       latex allrunes.ins
     Some 231 files are generated.
  5. Move all the 224 *.mf files to a suitable directory, preferably
       <font source base>/public/allrunes/
     which in a typical MiKTeX system would be
       C:\Local TeX Files\fonts\source\public\allrunes\
     In a texlive system it might be like
       /usr/local/share/texmf/fonts/source/public/allrunes/
  6. Move the 6 *.fd files and the file allrunes.sty
     to a suitable directory, preferably
       <tex base>/tex/latex/allrunes/
     which in a typical MiKTeX system would be
       C:\Local TeX Files\tex\latex\allrunes\
     In a typical texlive system it would be like
       /usr/local/share/texmf/tex/latex/allrunes/
  7. Refresh the file name database. In MiKTeX 2.9 you just would run
       initexmf --admin --update-fndb
     or find it somewhere in Start|Program|MiKTeX 2.9|Maintenance(Admin)|
        |Settings(Admin)...
     In texlive you would just run
       texhash
  8. Run the command
       latex allrunes.dtx
     to produce the documentation and test the installation.
     Run it one more time to resolve the references, before
     you view it.

INSTALLATION (OF THE TYPE1 FONT FILES)

     Installation of the type1 fonts requires the allrunes package
     to be installed according to the above description. Make sure
     that both LaTeX and dvips works fine with the Metafont
     fonts before you install the type1 fonts.

  1. Move all the files (named fru??.pfb) from the type1/pfb
     directory to a suitable directory, preferably
       <type1 font base>/public/allrunes
     which in a typical MiKTeX system would be
       C:\Local TeX Files\fonts\type1\public\allrunes\
     and in a texlive system it might be like
       /usr/local/share/texmf/fonts/type1/public/allrunes/
  2. Move the file allrunes.map from the type1 directory
     to some suitable directory, like
       <dvips base>/allrunes
     which in a typical MiKTeX system would be
       C:\Local TeX Files\fonts\map\dvips\allrunes\
     and in a texlive system it might be like
       /usr/local/share/texmf/fonts/map/dvips/allrunes/
  3. In a MiKTeX 2.9 system, run
       initexmf --admin --edit-config-file=updmap
     to edit the updmap.cfg-file; in that file, add the following line:
       MixedMap allrunes.map
     then Save, and Exit the editor.
     Then, in a MiKTeX system, refresh the file name database, see paragraph 7 above.
     In a texlive system, first refresh the file name database, see paragraph 7 above,
     then run the command:
       updmap-sys --enable MixedMap=allrunes.map
  4. Update the other .map files. In MiKTeX 2.9 you run
       initexmf --admin --mkmaps -v
     and in texlive you run
       update-updmap
       updmap-sys
  5. Run 
       latex allrunes.dtx
     then try both
        dvips -Ppk allrunes
     (which will use the bitmapped pk fonts) and
        dvips -Poutline allrunes
     (which will use the outline type1 fonts). You might also try
        pdflatex allrunes.dtx

