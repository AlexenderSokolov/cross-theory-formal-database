dnl  Process this file with autoconf to produce a configure script
AC_INIT(urlbst, 0.9.1, gray@nxg.name)
RELEASEDATE="2023 January 30"
AC_SUBST(RELEASEDATE)

AC_SUBST(REPOURL, [https://heptapod.host/nxg/urlbst])
AC_SUBST(CTANURL, [https://ctan.org/pkg/urlbst])

AC_REVISION(@PACKAGE_VERSION@)

dnl  COPYRIGHTYEARS="2002-03, 2005-12, 2014, 2019, 2022, 2023"
dnl  simpler...
COPYRIGHTYEARS="2002–23"
AC_SUBST(COPYRIGHTYEARS)

AC_PREREQ(2.50)

AC_CONFIG_SRCDIR([urlbst.in])

AC_PATH_PROG(PERL, perl)


dnl  Add --with-eprints: tune default support for eprints
WITHEPRINTS=1
AC_SUBST(WITHEPRINTS)
EPRINTURL=https://arxiv.org/abs/
AC_SUBST(EPRINTURL)

dnl  Add --with-doi: tune default support for DOI fields
WITHDOIRESOLVER=1
AC_SUBST(WITHDOIRESOLVER)
DOIURL=https://doi.org/
AC_SUBST(DOIURL)

dnl  Add --with-pubmed
WITHPUBMEDRESOLVER=1
AC_SUBST(WITHPUBMEDRESOLVER)
PUBMEDURL=http://www.ncbi.nlm.nih.gov/pubmed/
AC_SUBST(PUBMEDURL)

AC_ARG_WITH(eprints,
[  --with-eprints[[=url]]  Include eprint support by default, giving optional URL],
  if test "$withval" = "yes"; then
    WITHEPRINTS=1
  elif test "$withval" = "no"; then
    WITHEPRINTS=0
  else
    WITHEPRINTS=1
    EPRINTURL=$withval
  fi)

AC_ARG_WITH(doi,
[  --with-doi=[[=url]]     Include support for a DOI resolver by default, giving optional URL],
  if test "$withval" = yes; then
    WITHDOIRESOLVER=1
  elif test "$withval" = no; then
    WITHDOIRESOLVER=0
  else
    WITHDOIRESOLVER=1
    DOIURL=$withval
  fi)

AC_ARG_WITH(pubmed,
[  --with-pubmed=[[=url]]     Include support for a PUBMED resolver by default, giving optional URL],
  if test "$withval" = yes; then
    WITHPUBMEDRESOLVER=1
  elif test "$withval" = no; then
    WITHPUBMEDRESOLVER=0
  else
    WITHPUBMEDRESOLVER=1
    PUBMEDURL=$withval
  fi)


dnl  Add --with-href: set default support for hyperlinks
dnl  Default is to have no hyperlinks
WITHHREF=0
AC_SUBST(WITHHREF)

AC_ARG_WITH(href,
[  --with-href[[=int]]  Include eprint hyperlinks (0/1/2=none/hypertex/hyperref)],
  if test "$withval" = yes; then
    WITHHREF=2
  elif test "$withval" = no; then
    WITHHREF=0
  else
    WITHHREF=$withval
  fi)


AC_CONFIG_FILES(Makefile)
AC_CONFIG_FILES(urlbst, [chmod +x urlbst])

AC_OUTPUT
