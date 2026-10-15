% Copyright 2018 Nicholas Beaton
% 2020 version updated by Olya Mandelshtam
% 2021 version updated by Tomer Bauer
% 2022 version updated by Ben Salisbury
% 2025 version updated by Yasuhide NUMATA. (2024 -> 2025, 36 -> 37, Bochum -> Sapporo 2020/09/02 -> 2024/09/09)

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{FPSAC2025}[2024/09/09 FPSAC 2025 Proceedings class]

\newif \if@submission
\global \@submissionfalse
\DeclareOption{submission}{
  \global \@submissiontrue
}

\newif \if@revision
\global \@revisionfalse
\DeclareOption{revision}{
  \global \@submissiontrue
  \global \@revisiontrue
}

\newif \if@finalversion
\DeclareOption{finalversion}{
  \global \@submissiontrue
  \global \@revisiontrue
  \global \@finalversiontrue
}

\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}

\ProcessOptions\relax

\LoadClass[letterpaper,12pt]{article}

\usepackage[hyphens]{url}

\RequirePackage{calc}
\RequirePackage[top=1in,bottom=1in,left=1in,right=1in,includehead]{geometry}
\RequirePackage[dvipsnames,table]{xcolor}
\definecolor{rub-blau}{RGB}{0,53,96}
\definecolor{rub-grun}{RGB}{141, 174, 16}
\definecolor{fast-rub-blau}{RGB}{160,173,189}
\RequirePackage[colorlinks=true,citecolor=fast-rub-blau,linkcolor=rub-blau,urlcolor=rub-grun,breaklinks=true]{hyperref}
\Urlmuskip=0mu plus 3mu\relax
\RequirePackage{lastpage}

\RequirePackage{amsmath,amsthm,amssymb}
\RequirePackage{graphicx}
\RequirePackage{caption}
\RequirePackage{enumitem}
\RequirePackage{lmodern} % Rendering font compatibility for absent Palatino metrics.
\linespread{1.05}
\RequirePackage[T1]{fontenc}

\RequirePackage[capitalize,nameinlink,noabbrev]{cleveref}

% \setlength \textheight{56pc}
% \setlength \textwidth{35pc}
% \setlength \headsep{30\p@}
% \setlength \footskip{10\p@}
% \setlength \oddsidemargin{10\p@}
% \setlength \evensidemargin{21\p@}
% \setlength \textfloatsep{13\p@ \@plus 2\p@ \@minus 4\p@}
% \setlength \dbltextfloatsep{13\p@ \@plus 2\p@ \@minus 4\p@}
% \setlength \parskip{\z@ \@plus 1\p@}
% \setlength \parindent{10\p@}
% \setlength \topsep{4\p@ \@plus 2\p@ \@minus 1\p@}

\numberwithin{equation}{section}

\def\@title{\relax}
\def\@titlehead{\relax}
% pulling the title information from source
\def \title{\@ifnextchar[{\@gettitletwo}{\@gettitleone}}
\def \@gettitleone#1{\@gettitletwo[#1]{#1}}
\def \@gettitletwo[#1]#2{{
  \gdef \@title{#2}
  \def \\{\unskip \space \ignorespaces}
  \gdef \@titlehead{#1}
}}

\newif \if@marksrequired
\newcommand \addressmark[1]{%
  \if@marksrequired%
    $^{#1}$%
  \fi%
}
\global \@marksrequiredfalse
\gdef \and{\ignorespaces \space \@authorand \space \ignorespaces}
\gdef \@authorand{and}


\def\@author{\relax}
\def\@authorhead{\relax}
% pulling the author information from source
\def \author{\@ifnextchar[{\@getauthortwo}{\@getauthorone}}
\def \@getauthorone#1{\@getauthortwo[#1]{#1}}
\def \@getauthortwo[#1]#2{{
  \gdef \@author{#2}
  \def \\{\unskip \space \ignorespaces}
  \gdef \@authorhead{#1}
}}

\def\@address{\relax}
% pulling address information from source
\def \address{\@getaddress}
\def \@getaddress#1{{
  \gdef \@address{#1}
}}

\newif \if@keywordsgiven
\@keywordsgivenfalse
\def\@keywords{\relax}
% pulling keywords information from source
\def \keywords{\@getkeywords}
\def \@getkeywords#1{{
  \global \@keywordsgiventrue
  \gdef \@keywords{#1}
}}

\def \@received{\relax}
\newcommand \received[1]{
  \gdef\@received{Received #1}
}
\def \@revised{\relax}
\newcommand \revised[1]{
  \gdef\@revised{revised #1}
}
\def \@accepted{\relax}
\newcommand \accepted[1]{
  \def\@accepted{accepted #1}
}

\newif \if@abstractgiven
\@abstractgivenfalse
\def \@abstract{\relax}
\long\def \abstract#1{
  \global \@abstractgiventrue
  \long\gdef \@abstract{#1}
}

\newif \if@resumegiven
\@resumegivenfalse
\def \@resume{\relax}
\long\def \resume#1{
  \global \@resumegiventrue
  \long\gdef \@resume{#1}
}

\def \@resumetitle{\relax}
\long\gdef \@resumetitle{R\'esum\'e}
\long\def \resumetitle#1{
  \long\gdef \@resumetitle{#1}
}

\def \@articlenumber{YY}
\def \articlenumber#1{\gdef \@articlenumber{#1}}

%%%%%%% BIBLATEX STUFF %%%%%%%

% Rendering bibliography interface delegated to conventional BibTeX with original fields.
% Rendering-only BibLaTeX formatting omitted: \RequirePackage{doi}
% Rendering-only BibLaTeX formatting omitted: \renewcommand\mkbibnamelast[1]{#1}
% Rendering-only BibLaTeX formatting omitted: \renewbibmacro{in:}{}
% Rendering-only BibLaTeX formatting omitted: \DeclareFieldFormat[misc]{title}{\mkbibquote{#1}}
% Rendering-only BibLaTeX formatting omitted: \renewcommand*{\bibfont}{\small}
% Rendering-only BibLaTeX formatting omitted: \DeclareFieldFormat[article]{volume}{\mkbibbold{#1}}
% Rendering-only BibLaTeX formatting omitted: \DeclareFieldFormat{url}{\href{#1}{Link}}
% Rendering-only BibLaTeX formatting omitted: \DeclareFieldFormat{doi}{\href{https://dx.doi.org/#1}{\textsc{doi}}}
% Rendering-only BibLaTeX formatting omitted: \DeclareFieldFormat{eprint:arxiv}{\href{https://arxiv.org/abs/#1}{arXiv:\allowbreak{#1}}}
% Rendering-only BibLaTeX formatting omitted: \DeclareFieldFormat{eprint}{\href{https://arxiv.org/abs/#1}{arXiv:\allowbreak{#1}}}
% Rendering-only BibLaTeX formatting omitted: \AtEveryBibitem{\clearfield{issn}\clearfield{isbn}\clearlist{language}}
% print url if no doi
% Rendering-only BibLaTeX formatting omitted: \renewbibmacro*{doi+eprint+url}{%
% Rendering-only BibLaTeX formatting omitted:     \printfield{doi}%
% Rendering-only BibLaTeX formatting omitted:     \newunit\newblock%
% Rendering-only BibLaTeX formatting omitted:     \iftoggle{bbx:eprint}{%
% Rendering-only BibLaTeX formatting omitted:         \usebibmacro{eprint}%
% Rendering-only BibLaTeX formatting omitted:     }{}%
% Rendering-only BibLaTeX formatting omitted:     \newunit\newblock%
% Rendering-only BibLaTeX formatting omitted:     \iffieldundef{doi}{%
% Rendering-only BibLaTeX formatting omitted:         \usebibmacro{url+urldate}}%
% Rendering-only BibLaTeX formatting omitted:         {}%
% Rendering-only BibLaTeX formatting omitted: }


\def\abx@missing@entry#1{\abx@missing{#1??}}

%%%%%%%%%%%%%%


\let \pagenumber=\@gobble

\AtBeginDocument{
\gdef \@thefirstpage{\thepage}
\hypersetup{pdftitle={\@title},pdfauthor={\@author}}
}

\long \gdef \@firsthead{\parbox{\textwidth}{\footnotesize \textit{Accepted manuscript} \hfill \textit{Proceedings of the 37\textsuperscript{th} Conference on Formal Power} \newline \phantom{..} \hfill \textit{Series and Algebraic Combinatorics (Sapporo)}}}


\def \ps@first{
  \def \@evenhead{\normalfont \@firsthead \hss}
  \def \@oddhead{\normalfont \@firsthead \hss }
}

\global \@twosidetrue

\def \ps@journal{
  \let \@mkboth \@gobbletwo
  \def \@evenhead{
    \def \thanks####1{\relax}%
    \small \thepage \hfill \textit{\@authorhead}
  }
  \def \@oddfoot{}
  \def \@oddhead{
    \small \textit{\@titlehead} \hfill \thepage
  }
  \def \@evenfoot{}
}

\renewcommand \maketitle{
  \thispagestyle{first}
  \renewcommand \thefootnote{\fnsymbol{footnote}}
  \@maketitle
  \@thanks
  \renewcommand\thefootnote{\arabic{footnote}}

  \@makeabstract
  \setcounter{footnote}{0}
}

\newcommand \printkeywords{
  \small \noindent \textbf{Keywords:} \@keywords \par
}

\newenvironment{titlesp}{
  \list{}{
    \leftmargin 0pt
  }\item[]
}{\endlist}

\newenvironment{abstractsp}{
  \list{}{
    \leftmargin 25pt
    \rightmargin 25pt
  }\item[]
}{\endlist}

\def \@maketitle{
  \begin{titlesp}
    \begingroup
    \hypersetup{hidelinks}
    \@marksrequiredtrue
    \null % this is a very annoying way to add space before the title
    \vspace{-19\p@}
    {\centering \hyphenpenalty=\@M \LARGE \@title \par}
    \vspace{12\p@}
    {\centering \large \@author \par}
    \vspace{6\p@}
%    {\centering \small \itshape \@address \par}
    \begin{abstractsp} {\small \itshape \@address \par} \end{abstractsp}
%    {\small \itshape \@address \par}
%    \vspace{6\p@}
%    \if@submission{\small{\@received}}\fi%
%    \if@revision{\small{; \@revised}}\fi%
%    \if@finalversion{\small{; \@accepted}}\fi%
%    \if@submission{\small{.}\vspace{0\p@}}\fi
    % \hrule \@height 1\p@
    \endgroup
  \end{titlesp}
}

\def \@makeabstract{
  \begin{abstractsp}
    \vspace{-10\p@}
    \bgroup
    \small
    \if@abstractgiven{\noindent{\textbf{Abstract.} \@abstract \par}}\fi
    \if@resumegiven{\noindent{\textbf{\@resumetitle.} \@resume \par}}\fi
    \if@keywordsgiven{\printkeywords}\fi
    \egroup
  \end{abstractsp}
  % \vspace{8\p@}
  % \hrule \@height 1\p@
}

\pagestyle{journal}

\newlength{\capsize}
%\setlength{\capsize}{\textwidth-50pt}

\long \def \@makecaption#1#2{%
%\newlength{\capsize}
\setlength{\capsize}{\textwidth-50pt}
  \sbox\@tempboxa{#2}
  \ifdim \wd\@tempboxa = 0pt
    \def \thistype{#1}
  \else
    \def \thistype{#1:}
  \fi
  \vskip \abovecaptionskip%
  \small%
  \sbox \@tempboxa{\textbf{\thistype} #2}%
  \ifdim \wd \@tempboxa > \capsize%
    \begin{center}
    \begin{minipage}{\capsize}
      \textbf{\thistype} #2 \par
    \end{minipage}
    \end{center}
  \else%
    \global \@minipagefalse%
    \hb@xt@ \hsize{\hfil \box\@tempboxa \hfil}%
  \fi%
  \vskip \belowcaptionskip%
}

\newcommand \acknowledgments{\section*{Acknowledgments}}
\newcommand \acknowledgements{\section*{Acknowledgements}}
\newcommand \noabstract{\printkeywords}

%cref names for multiple refs
%
%
\crefname{example}{Example}{Examples}
\crefname{theorem}{Theorem}{Theorems}
\crefname{lemma}{Lemma}{Lemmas}
\crefname{proposition}{Proposition}{Propositions}
\crefname{thm}{Theorem}{Theorems}
\crefname{lem}{Lemma}{Lemmas}
\crefname{prop}{Proposition}{Propositions}
\crefname{figure}{Figure}{Figures}
\crefname{fig}{Figure}{Figures}
\crefname{remark}{Remark}{Remarks}
\crefname{rem}{Remark}{Remarks}
\crefname{cor}{Corollary}{Corollaries}
\crefname{corollary}{Corollary}{Corollaries}
\crefname{conjecture}{Conjecture}{Conjectures}
\crefname{conj}{Conjecture}{Conjectures}
\crefname{ex}{Example}{Examples}


\endinput
% end of file
