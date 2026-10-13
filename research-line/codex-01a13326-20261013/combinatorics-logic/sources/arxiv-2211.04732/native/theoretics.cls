%%
%% This is file `theoretics.cls'.
%%
%% Some info about author and license goes here.
%%
\NeedsTeXFormat{LaTeX2e}
\def\@ThCSversionnum{0.91 }
\def\@ThCSversiondate{2025/06/17 }
\ProvidesClass{theoretics}[\@ThCSversiondate v\@ThCSversionnum TheoretiCS class]
%  Added automatic DOI, bibliography tweaks, metadata

\LoadClass{article}

% Prevent the eventual "Too many alphabets" error
\newcommand\hmmax{0}
\newcommand\bmmax{0}


% Load early to avoid collisions
\RequirePackage{amsmath}
\RequirePackage{amsthm}
\RequirePackage{amssymb}
\RequirePackage{thmtools}

% Package for printing numbers
\RequirePackage{xfp}

\renewcommand{\title}[1]{\gdef\@title{#1}\gdef\@ThCStitle{#1}}%  Added by Miguel

% Paul,  The following package is supposed to have been incorporated into the latest Latex2e that came out in June but it isn't working right yet in Overleaf
\RequirePackage{textcase}

% Package to allow more optional author parameters
\RequirePackage{xargs}

%Authorformatting options
\newif\if@authorindent
\@authorindenttrue
\newif\if@longft
\@longftfalse

% Public commands
\newif\if@ThCSreceived
\newif\if@ThCSrevised
\newif\if@ThCSaccepted
\newif\if@ThCSpublished
\newif\if@ThCSupdated
\newif\if@ThCSkeywords
\newif\if@ThCSdoi
\newif\ifThCSdoicreated
\newif\if@ThCSlinebreak
\newif\if@ThCSthanks
\newif\if@ThCSshortnames
\newif\if@ThCSshorttitle
\newif\if@ThCSyear 
\newif\if@ThCSarticlenum
\newif\ifThCSciteas
\@ThCSreceivedfalse
\@ThCSrevisedfalse
\@ThCSacceptedfalse
\@ThCSpublishedfalse
\@ThCSupdatedfalse
\@ThCSkeywordsfalse
\@ThCSdoifalse
\ThCSdoicreatedfalse
\@ThCSlinebreakfalse
\@ThCSthanksfalse
\@ThCSshortnamesfalse
\@ThCSshorttitlefalse
\@ThCSyearfalse
\@ThCSarticlenumfalse
\ThCSciteastrue
\newcommand\ThCSreceived[1]{\def\@ThCSreceived{#1}\@ThCSreceivedtrue\@ThCSlinebreaktrue}
\newcommand\ThCSrevised[1]{\def\@ThCSrevised{#1}\@ThCSrevisedtrue\@ThCSlinebreaktrue}
\newcommand\ThCSaccepted[1]{\def\@ThCSaccepted{#1}\@ThCSacceptedtrue\@ThCSlinebreaktrue}
\newcommand\ThCSpublished[1]{\def\@ThCSpublished{#1}\@ThCSpublishedtrue\@ThCSlinebreaktrue}
\newcommand\ThCSupdated[1]{\def\@ThCSupdated{#1}\@ThCSupdatedtrue\@ThCSlinebreaktrue}
\newcommand\ThCSkeywords[1]{\def\@ThCSkeywords{#1}\@ThCSkeywordstrue}
\newcommand\ThCSdoi[1]{\def\@ThCSdoi{#1}\@ThCSdoitrue}
\newcommand\ThCSthanks[1]{\def\@ThCSthanks{#1}\@ThCSthankstrue}
\newcommand\ThCSshortnames[1]{\def\@ThCSshortnames{#1}\@ThCSshortnamestrue}
% Added ThCSshorttitle
\newcommand\ThCSshorttitle[1]{\def\@ThCSshorttitle{#1}\@ThCSshorttitletrue}
\newcommand\ThCSyear[1]{\def\@ThCSyear{#1}\@ThCSyeartrue}
\newcommand\ThCSarticlenum[1]{\def\@ThCSarticlenum{#1} \@ThCSarticlenumtrue}
\newcommand\@ThCSvolume{\if@ThCSyear {\inteval{\@ThCSyear - 2021}}
        \else X \fi}

\RequirePackage{etoolbox}
\RequirePackage{refcount}

% Private commands
\newcommand\@ThCSlightlogo{logo_lightred.pdf}
\newcommand\@ThCSdarklogo{logo_darkred.pdf}
\newcommand\@ThCSfrontlogo{\includegraphics[width=160pt]{\@ThCSlightlogo}}
%\newcommand\@ThCSheadlogo{\includegraphics[width=64pt]{\@ThCSdarklogo}} % Original version from Miguel
\newcommand\@ThCSheadlogo{\includegraphics[width=72pt]{\@ThCSdarklogo}}
\newcommand\@ThCSfirstcolwidth{384pt}
\newcommand\@ThCSsecondcolwidth{160pt}
%\newcommand\@ThCSsubcolwidth{176pt} %Original grid from Miguel
%\newcommand\@ThCSsubcolwidth{192pt}% Modified grid from Paul
\newcommand\@ThCSsubcolwidth{352pt}
%\newcommand\@ThCSauthorsrulewidth{352pt}
\newcommand\@ThCSauthorsrulewidth{384pt}
\def\hidden@ampersand{&}%

% Footer in the last page. Declaring so early to avoid other packages to break page.
\AtEndDocument{
\FloatBarrier
%\vfill
%\makeatletter
%\setlength{\@fpbot}{0pt}
%\makeatother
%\setlength{\footskip}{0pt}
%\begin{table}[b]
%\noindent
%{\fontsize{16}{12}\selectfont \textcolor{@ThCSlightred}{\textls*{\interextrabold \if@ThCSyear \@ThCSyear \else XXXX\fi:\if@ThCSarticlenum \@ThCSarticlenum \else XX \fi}}}%
%\hfill
%\@ThCSfrontlogo \\
%{\color{@ThCSlightred}\rule{\textwidth}{3pt}\vspace*{.5em}} \\
%{\raggedright\textcolor{@ThCSdarkred}{%
%\sffamily\fontsize{10}{12}\selectfont
%This work is licensed under the Creative Commons Attribution 4.0    International License.\\ 
 %   To view a copy of this license, visit
%    http://creativecommons.org/licenses/by/4.0/ \\
%    or send a letter to
%    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA. \\
%    \ \\
%{\normalfont\copyright}\ \ThCS@footauthors.\\
%}}%
%\end{table}
\fancyfoot[L]{%
{\fontsize{14.4}{12}\selectfont \textcolor{@ThCSlightred}{\textls*{\interextrabold \if@ThCSyear \@ThCSyear \else XXXX\fi:\if@ThCSarticlenum \@ThCSarticlenum \else XX \fi}}}%
\hfill
%\@ThCSfrontlogo 
\includegraphics[width=120pt]{\@ThCSlightlogo}
\\[-12pt]
% Choose alternative final copyright footer depending on length of author list
\expandarg\StrLen{\ThCS@footauthors}[\@authorlen]
\ifnum\@authorlen>100
% author list too long to fit on one line so use minipages for footer
{\color{@ThCSlightred}\rule{\textwidth}{3pt}\vspace*{3pt}}
    \\[-10pt]%
    {\raggedright\textcolor{@ThCSdarkred}{%
    \sffamily\fontsize{10}{12}\selectfont%
   \begin{minipage}[t]{255pt}
   This work is licensed under the Creative Commons\\ 
   Attribution 4.0 International License.\\ 
%   To view a copy of this license, visit
   http://creativecommons.org/licenses/by/4.0/
%\\
% or send a letter to
%  Creative Commons, PO Box 1866, Mountain View, CA 94042, USA. 
   \end{minipage}
 %  \hfill
  \begin{minipage}[t]{318pt}
{\hyphenpenalty=10000\exhyphenpenalty=10000}{\normalfont\copyright}\ \ThCS@footauthors.\hfill
  \end{minipage}}}
\else
% Author list short enough for copyright list to fit on one line at end.
{\color{@ThCSlightred}\rule{\textwidth}{3pt}\vspace*{3pt}} \\
{\raggedright\textcolor{@ThCSdarkred}{%
\sffamily\fontsize{10}{12}\selectfont
This work is licensed under the Creative Commons Attribution 4.0
    International License.\\ 
 %   To view a copy of this license, visit
    http://creativecommons.org/licenses/by/4.0/
    %\\
   % or send a letter to
  %  Creative Commons, PO Box 1866, Mountain View, CA 94042, USA. 
  \\[-10pt]
{\normalfont\copyright}\ \ThCS@footauthors.\hfill}}
\fi
}
}


% Fonts
\RequirePackage{fontsize}
%\changefontsize[24pt]{14.4pt}   Original version from Miguel
\changefontsize[22pt]{14.4pt}

% Paper size and margins
\RequirePackage[paperheight=1024pt,paperwidth=768pt,hmargin=96pt,top=96pt,bottom=96pt,headheight=24pt,headsep=32pt,footskip=36pt]{geometry}

\RequirePackage{notomath}
\RequirePackage{inter}
\RequirePackage[scaled=0.85]{DejaVuSansMono}
\def\bfseries@rm{sb}

\DeclareMathVersion{sansmath}
\SetSymbolFont{operators}{sansmath}{OT1}{NotoSans-TLF}{m}{n}
\SetSymbolFont{letters}{sansmath}{OML}{notosansmi}{m}{it}
\SetMathAlphabet\mathbf{sansmath}{OT1}{NotoSans-TLF}{b}{n}
\SetMathAlphabet\mathsf{sansmath}{OT1}{NotoSans-TLF}{m}{n}
\SetMathAlphabet\mathit{sansmath}{OT1}{NotoSans-TLF}{m}{it}

\DeclareMathVersion{sansmathbold}
\SetSymbolFont{operators}{sansmathbold}{OT1}{NotoSans-TLF}{b}{n}
\SetSymbolFont{letters}{sansmathbold}{OML}{notosansmi}{b}{it}
\SetSymbolFont{symbols}{sansmathbold}{LMS}{ntxsy}{b}{n}
\SetMathAlphabet\mathbf{sansmathbold}{OT1}{NotoSans-TLF}{b}{n}
\SetMathAlphabet\mathsf{sansmathbold}{OT1}{NotoSans-TLF}{b}{n}
\SetMathAlphabet\mathit{sansmathbold}{OT1}{NotoSans-TLF}{b}{it}


% Upright Greek letters uppercase
\DeclareMathSymbol{\Gamma}{\mathord}{operators}{0}
\DeclareMathSymbol{\Delta}{\mathord}{operators}{1}
\DeclareMathSymbol{\Theta}{\mathord}{operators}{2}
\DeclareMathSymbol{\Lambda}{\mathord}{operators}{3}
\DeclareMathSymbol{\Xi}{\mathord}{operators}{4}
\DeclareMathSymbol{\Pi}{\mathord}{operators}{5}
\DeclareMathSymbol{\Sigma}{\mathord}{operators}{6}
\DeclareMathSymbol{\Upsilon}{\mathord}{operators}{7}
\DeclareMathSymbol{\Phi}{\mathord}{operators}{8}
\DeclareMathSymbol{\Psi}{\mathord}{operators}{9}
\DeclareMathSymbol{\Omega}{\mathord}{operators}{10}

% Italic Greek letters lowercase
\DeclareMathSymbol{\alpha}{\mathord}{letters}{11}
\DeclareMathSymbol{\beta}{\mathord}{letters}{12}
\DeclareMathSymbol{\gamma}{\mathord}{letters}{13}
\DeclareMathSymbol{\delta}{\mathord}{letters}{14}
\DeclareMathSymbol{\epsilon}{\mathord}{letters}{15}
\DeclareMathSymbol{\zeta}{\mathord}{letters}{16}
\DeclareMathSymbol{\eta}{\mathord}{letters}{17}
\DeclareMathSymbol{\theta}{\mathord}{letters}{18}
\DeclareMathSymbol{\iota}{\mathord}{letters}{19}
\DeclareMathSymbol{\kappa}{\mathord}{letters}{20}
\DeclareMathSymbol{\lambda}{\mathord}{letters}{21}
\DeclareMathSymbol{\mu}{\mathord}{letters}{22}
\DeclareMathSymbol{\nu}{\mathord}{letters}{23}
\DeclareMathSymbol{\xi}{\mathord}{letters}{24}
\DeclareMathSymbol{\pi}{\mathord}{letters}{25}
\DeclareMathSymbol{\rho}{\mathord}{letters}{26}
\DeclareMathSymbol{\sigma}{\mathord}{letters}{27}
\DeclareMathSymbol{\tau}{\mathord}{letters}{28}
\DeclareMathSymbol{\upsilon}{\mathord}{letters}{29}
\DeclareMathSymbol{\phi}{\mathord}{letters}{30}
\DeclareMathSymbol{\chi}{\mathord}{letters}{31}
\DeclareMathSymbol{\psi}{\mathord}{letters}{32}
\DeclareMathSymbol{\omega}{\mathord}{letters}{33}
\DeclareMathSymbol{\varepsilon}{\mathord}{letters}{34}
\DeclareMathSymbol{\vartheta}{\mathord}{letters}{35}
\DeclareMathSymbol{\varpi}{\mathord}{letters}{36}
\DeclareMathSymbol{\varrho}{\mathord}{letters}{37}
\DeclareMathSymbol{\varsigma}{\mathord}{letters}{38}
\DeclareMathSymbol{\varphi}{\mathord}{letters}{39}


% tabularx
\RequirePackage{tabularx}
\newcommand{\@HY}{\hyphenpenalty=10000\exhyphenpenalty=10000}
\newcolumntype{Q}{>{\setlength{\baselineskip}{15pt}\@HY\raggedright\arraybackslash\hsize=\@ThCSsubcolwidth}X} % Author names original from Miguel
\newcolumntype{R}{>{\setlength{\baselineskip}{12pt}\@HY\raggedright\arraybackslash\hsize=\@ThCSfirstcolwidth}X} % Author wrapper
%\newcolumntype{Y}{>{\setlength{\baselineskip}{40pt}\@HY\raggedright\arraybackslash\hsize=\@ThCSfirstcolwidth}X} % Main title  original from Miguel no longer used
\newcolumntype{Z}{>{\setlength{\baselineskip}{12pt}\@HY\raggedright\arraybackslash\hsize=\@ThCSsecondcolwidth}X} % Side info 


% Default indent
\setlength\parindent{32pt}

% Last page reference
%\RequirePackage{lastpage}
\RequirePackage{pageslts}
\pagenumbering{arabic}

% Support for includegraphics
\RequirePackage{graphicx}
\graphicspath{./}

% Change font tracking
\RequirePackage[letterspace=150]{microtype}

% Page breaking
\widowpenalty=10000
\clubpenalty=10000

% Custom colors
%\RequirePackage{color}% Original version from Miguel
\RequirePackage[RGB,svgnames]{xcolor}% Changed by Paul to give more flexibility and broader compatability
\definecolor{@ThCSlightred}{RGB}{255,35,45}
\definecolor{@ThCSdarkred}{RGB}{195,30,30}

% Title styling
\RequirePackage{titlesec}

%\titleformat{\paragraph}[runin]
%{\lsstyle\interextrabold\mathversion{sansmathbold}\fontsize{12}{12}\selectfont}
%{}
%{1em}
%{\MakeTextUppercase}  % Emilka's original \paragraph design, which has problems because of the loose spacing of math.

\titleformat{\paragraph}[runin]{\intersemibold\mathversion{sansmathbold}\fontsize{14.4}{14.4}\selectfont}{\thesubparagraph}{1em}{}% Version changed by Paul

%\titleformat{\subparagraph}[runin]{\bf}{\thesubparagraph}{1em}{}[:]% First test version added by Paul
%\titleformat{\subparagraph}[runin]{\intersemibold\mathversion{sansmathbold}\fontsize{14.4}{14.4}\selectfont}{\thesubparagraph}{1em}{}% Original version added by Paul that is now \paragraph

\titleformat{\subparagraph}[runin]{\intermedium\mathversion{sansmath}\fontsize{14.4}{14.4}\selectfont}{\thesubparagraph}{1em}{}% Added by Paul


    
\titleformat{\section}
% {\interextrabold\mathversion{sansmathbold}\fontsize{15}{12}\selectfont}  Original version from Miguel
{\interextrabold\mathversion{sansmathbold}\fontsize{17.28}{18}\selectfont}
{\thesection.}
{1.5em}
{}

\titleformat{name=\section,numberless}
% {\interextrabold\mathversion{sansmathbold}\fontsize{15}{12}\selectfont}  Original version from Miguel
{\interextrabold\mathversion{sansmathbold}\fontsize{17.28}{18}\selectfont}
{}
{32pt}
{}

\titleformat{\subsection}
{\intersemibold\mathversion{sansmathbold}\fontsize{15}{12}\selectfont}
{\thesubsection}
{1em}
{}

\titleformat{\subsubsection}
%{\sffamily\mathversion{sansmath}\fontsize{15}{12}\selectfont}%  Original version from Miguel
{\intersemibold\mathversion{sansmath}\fontsize{14.4}{12}\selectfont} 
{\thesubsubsection}
{1em}
{}

% Formatting for \part added by Paul
\titleformat{\part}
{\interextrabold\mathversion{sansmath}\fontsize{20}{22}\selectfont\color{@ThCSdarkred}%\filcenter%  No longer center with things in red
} 
{Part \thepart:}
{1em}
{}

%\titlespacing{\paragraph}{0pt}{3.25ex}{.5em}[]%original from Miguel
\titlespacing*{\paragraph}{0pt}{18pt}{.5em}[]
\titlespacing*{\subparagraph}{0pt}{15pt}{.5em}[]% Added by Paul
%\titlespacing*\section{0pt}{24pt}{24pt}    Original version from Miguel
\titlespacing*\section{0pt}{30pt}{18pt}
\titlespacing*\subsection{0pt}{24pt}{12pt}
\titlespacing*\subsubsection{0pt}{24pt}{12pt}

% Added by Paul
\titlespacing*{\part}{0pt}{38pt}{24pt}
%

\pretocmd{\section}{%
    \ifnum\value{section}=0
%       \if@pageonerules
%       {\noindent\color{@ThCSlightred}%
%       \rule{\textwidth}{3pt}%
%        }%
%        \else
        \vskip 44pt
%       \fi
    \fi
}{}{}

% Abstract
\RequirePackage{environ}
%\AtEndEnvironment{abstract}{\@restore@}% Command from Miguel removed.   Also edited out code that decides between sidebar \ThCSthanks beside abstract or not.   Following code by Thomas Schwentick that does simple full width abstract and \ThCSthanks as unmarked footnote.

%\RenewEnviron{abstract}{%
%\paragraph{Abstract.}{{\let\thefootnote\relax\footnote{\@ThCSthanks}}\BODY}% TS
%}%

\RenewEnviron{abstract}{%
\paragraph{\lsstyle\interextrabold\fontsize{12}{12}\selectfont\MakeTextUppercase{Abstract.}}%
%\if@ThCSthanks{{\let\thefootnote\relax\footnote{\hspace{-32pt}\parbox[t]{\dimexpr\@ThCSfirstcolwidth+\@ThCSsecondcolwidth+32pt}%
%{\@ThCSthanks}}}%
%\setcounter{footnote}{0}}\fi 
\BODY% 
}%




% Lists
\RequirePackage[shortlabels]{enumitem}
\setlist{noitemsep}
\setlist[itemize]{label={\hspace*{8pt}\parbox{16pt}{\rule{16pt}{1pt}}},leftmargin=*,labelsep=8pt,topsep=0pt}
% \setlist[enumerate]{label={\hspace*{8pt}\parbox{16pt}{\raggedleft\arabic*.}},leftmargin=*,labelsep=8pt,topsep=0pt} % Original version from Miguel
% Added by Paul modified by suggestion from Thomas. Different default enumerate labels based on the level of indentation rather than only numeric.
\setlist[enumerate]{labelindent=16pt, labelwidth=8pt, 
leftmargin=*,labelsep=8pt,topsep=0pt}
\setlist[enumerate,1]{label={\arabic*.},ref={\arabic*}}
\setlist[enumerate,2]{label={\alph*.},ref={\alph*}}
\setlist[enumerate,3]{label={\roman*.},ref={\roman*}}
%\setlist[1]{after={\bigskip}}
\setlist[1]{after={\vspace*{7pt}}}

% Theorems
\newtheoremstyle{standard}
{}
{}
{}
{}
{\interextrabold\fontsize{12}{12}\selectfont}
{.}
{.5em}
%{{\MakeUppercase{\lsstyle\thmname{#1 }}}{\lsstyle\thmnumber{#2}}{\thmnote{ (#3)}}}% Revised from Miguel 9/11/2022
{{\MakeUppercase{\lsstyle\thmname{#1 }}}{\lsstyle\thmnumber{#2}}{\thmnote{ {\normalfont\bf\fontsize{14.4}{14.4}\selectfont (#3)}}}}

\newtheoremstyle{italicized}
{}
{}
{\itshape}
{}
{\interextrabold\fontsize{12}{12}\selectfont}
{.}
{.5em}
%{{\MakeUppercase{\lsstyle\thmname{#1 }}}{\lsstyle\thmnumber{#2}}{\thmnote{ (#3)}}}% Revised from Miguel 9/11/2022
{{\MakeUppercase{\lsstyle\thmname{#1 }}}{\lsstyle\thmnumber{#2}}{\thmnote{ {\normalfont\bf\fontsize{14.4}{14.4}\selectfont (#3)}}}}

\newcommand\ThCSnewtheostd[1]{%
\declaretheorem[style=standard,sibling=theorem,name=#1]{#1}
}

\newcommand\ThCSnewtheoita[1]{%
\declaretheorem[style=italicized,sibling=theorem,name=#1]{#1}
}

\declaretheorem[style=italicized,name=Theorem,numberwithin=section]{theorem}
\declaretheorem[style=italicized,sibling=theorem,name=Lemma]{lemma}
\declaretheorem[style=standard,sibling=theorem,name=Example,qed={\rotatebox[origin=c]{45}{$\blacksquare$}}]{example}

\ThCSnewtheoita{corollary}
\ThCSnewtheoita{proposition}

%\declaretheoremstyle[headfont=\lsstyle\interextrabold\fontsize{12}{12}\selectfont,notefont=\bf]{std}
%\declaretheorem[style=std,sibling=theorem,name=Definition]{definition}

\ThCSnewtheostd{definition}
%\ThCSnewtheostd{observation}  %Original from Miguel
\ThCSnewtheoita{observation}  
\ThCSnewtheoita{claim}    % Added by Paul
\ThCSnewtheoita{conjecture}  % Added by Paul
\ThCSnewtheoita{fact}   % Added by Paul
\declaretheorem[style=italicized,sibling=theorem,name=Open Problem]{open}  %  Added by Paul
\ThCSnewtheostd{construction}   % Added by Paul
\ThCSnewtheostd{remark}   % Added by Paul

% Unnumbered claim added by Paul
\declaretheorem[style=italicized,numbered=no,name={Claim\kern-.09em}]{claim*}

% subordinate numbered "techclaim" for use as a claim inside proofs.  Use with subproof environment instead of proof.
\declaretheorem[style=standard,sibling=theorem,name=Claim,numberwithin=theorem]{techclaim}

% Paul redefined proof environment modified from amsthm.sty so that all modifications of the proof label will come out correctly.
\renewenvironment{proof}[1][\proofname]{\par
  \pushQED{\qed}%
  \normalfont
  \topsep6\p@\@plus6\p@ \trivlist
  \item[\hskip\labelsep%\itshape #1 % original font from amsthm.sty
  \normalfont\lsstyle\interextrabold\mathversion{sansmath}\fontsize{12}{12}\selectfont\MakeTextUppercase{#1}% %new font for TheoretiCS
    \@addpunct{.}]\ignorespaces
}{%
  \popQED\endtrivlist
}

\renewcommand{\qedsymbol}{\textcolor{@ThCSdarkred}{$\blacksquare$}}

\newcommand{\subqedsymbol}{\textcolor{@ThCSdarkred}{\rotatebox[origin=c]{45}{$\blacksquare$}}}

% subproof environment added by Paul with modification by Thomas
\newenvironment{subproof}[1][\proofname]{\par
\renewcommand{\qedsymbol}{\subqedsymbol}
\pushQED{\qed}
  \normalfont
  \topsep6\p@\@plus6\p@ \trivlist
  \item[\hskip\labelsep
  \intersemibold\mathversion{sansmathbold}\fontsize{14.4}{14.4}\selectfont #1%
    \@addpunct{.}]\ignorespaces
}{%
  %{\subqedsymbol}
  \popQED
  \endtrivlist
}

% Math display formatting seems to add an extra blank character to footer
%\apptocmd{\normalsize}{\setlength{\abovedisplayskip}{11pt}\setlength{\belowdisplayskip}{11pt}\setlength{\abovedisplayshortskip}{0pt}  \setlength{\belowdisplayshortskip}{11pt}}{}{}

%Math displayskip formatting requiring an update to normalsize. Doing this with \apptocmd generated an extra blank character.  The current version was obtained by editing version from \typeout{\normalsize}
\renewcommand{\normalsize}{\relax \fontsize {14.4pt}{22.0pt}\selectfont%
\setlength{\abovedisplayskip}{11pt}%
\setlength{\abovedisplayshortskip}{0pt}%
\setlength{\belowdisplayskip}{11pt}%
\setlength{\belowdisplayshortskip}{11pt}%
\let \leftmargin \leftmargini
\topsep 14.66745pt plus 3.66745pt minus 7.33255pt
\parsep 7.33255pt plus 3.66745pt minus 1.83255pt
\itemsep \parsep
\leftmargin \leftmargini \topsep 14.66745pt plus 3.66745pt minus 7.33255pt\parsep 7.33255pt plus 3.66745pt minus 1.83255pt\itemsep \parsep}

% Remove vertical space before subequations
\AtBeginEnvironment{subequations}{\ifhmode\unskip\fi}


% Footnotes
\RequirePackage[bottom]{footmisc}

\renewcommand{\footnoterule}{%
  {\color{@ThCSlightred}\hrule width \textwidth height 2pt}
  \kern 9pt
}
\renewcommand{\@makefnmark}{%
    {\interextrabold\textcolor{@ThCSdarkred}{\footnotesize\textsuperscript{\hspace*{1pt}\@thefnmark}}}%  Original from Miguel
    %\intersemibold\textcolor{@ThCSdarkred}{\footnotesize\textsuperscript{\hspace*{1pt}\@thefnmark}}}%
}
% Paul added flag
\newif\if@infootnote
\@infootnotefalse
\renewcommand{\@makefntext}[1]{%
    \kern 3pt\parbox[t]{32pt}{\sffamily\fontsize{10}{12}\selectfont\raggedright\textcolor{@ThCSdarkred}{\@thefnmark}}%
    \@infootnotetrue
    \parbox[t]{\dimexpr\@ThCSfirstcolwidth+\@ThCSsecondcolwidth}{\sffamily\fontsize{10}{12}\selectfont\textcolor{@ThCSdarkred}{#1}
    \@infootnotefalse}%
}

% Headers and footers
\RequirePackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}

% To get length of a string
\RequirePackage{xstring}

% To change page margins
\RequirePackage{changepage}

% Package to detect location on page
\RequirePackage{zref-savepos}

% Support for author affiliations and emails
\newcommand\Authfont{\intersemibold\fontsize{15}{12}\selectfont} 
\newcommand\Emailfont{\normalfont\sffamily\fontsize{10}{12}\selectfont}
\RequirePackage[misc]{ifsym} % added by Paul to get envelope symbol \Letter
\RequirePackage{fontawesome5}% added by Paul to get ORCID iD symbol
\newcommand\Orcidfont{\normalfont\sffamily\fontsize{10}{12}\selectfont}
\def\orcidsymbol{\textcolor{@ThCSlightred}{\Orcidfont \faOrcid}}%
\newlength{\affilsep}\setlength{\affilsep}{10pt}
\newlength{\@affilsep}
\newcounter{Maxaffil}
\setcounter{Maxaffil}{3}
\newcounter{authors}
\newcounter{affil}
\newcounter{manaffil}
\newif\ifnewaffil \newaffiltrue
\newcommand\ThCS@authnote[1]{\textcolor{@ThCSdarkred}{\textsuperscript{\textbf{\textit{#1}}}}}
\newcommand\ThCS@affilnote[1]{\textbf{#1}}
\newcommand\ThCS@blk@and{\protect\Authfont\protect\ThCS@setsep}
\newcommand\ThCS@pand{\protect\and \protect\Authfont \protect\ThCS@setsep}
\@namedef{@sep1}{}
\@namedef{@sep2}{}
\newcommand\ThCS@affilsep{\protect\linebreak\protect\linebreak}
\newcommand\ThCS@setsep{\setlength{\@affilsep}{\affilsep}}
\newcommand\ThCS@resetsep{\setlength{\@affilsep}{\z@}}
\newcommand\ThCS@authlist{}
\newcommand\ThCS@affillist{}
\newcommand\ThCS@authors{}
\newcommand\ThCS@footauthors{}% New command from Miguel for Cite As
\xdef\ThCS@author{\noexpand\ThCS@blk@and\@author}
%\newcommand\ThCSauthor[3][]%
\newcommandx\ThCSauthor[4][1,4,usedefault]%
    %{\ifnewaffil\addtocounter{affil}{1}%   Old version replaced by Miguel
    {\ifnum\value{authors}>0\relax
    \g@addto@macro\ThCS@footauthors{, #2}
    \else
    \g@addto@macro\ThCS@footauthors{#2}
    \fi
    \def\ThCS@tmpnote{}%
    \renewcommand*{\do}[1]{
    \ifnewaffil\addtocounter{affil}{1}%
    \edef\ThCS@thenote{\alph{affil}}\fi
     %\if\relax##1\relax\def\ThCS@note{\ThCS@thenote}\else
     \def\ThCS@note{##1}%
        \ifcsundef{note##1}{%
            \addtocounter{manaffil}{1}%
            \csedef{note##1}{\alph{manaffil}}%
        }{}%
        \g@addto@macro\ThCS@tmpnote{,\csuse{note##1}}%
        \setcounter{Maxaffil}{0}%
    %\fi
     \StrSubstitute[1]{\ThCS@tmpnote}{,}{}[\ThCS@note]
    }
   %\docsvlist{#1}
    \if\relax#1\relax%
       \ifnewaffil\addtocounter{affil}{1}%
       \edef\ThCS@thenote{\alph{affil}}\fi%
       \def\ThCS@note{\ThCS@thenote}%
    \else\docsvlist{#1}%
    \fi%
    \ifnum\value{authors}>1\relax
    \@namedef{@sep\number\c@authors}{}\fi
    \addtocounter{authors}{1}%
    \begingroup
        \let\protect\@unexpandable@protect \let\and\ThCS@pand
        \def\thanks{\protect\thanks}\def\footnote{\protect\footnote}%
        \@temptokena=\expandafter{\ThCS@authors}%
        {\def\\{\protect\\[\@affilsep]
            \protect\ThCS@resetsep}%
            \xdef\ThCS@author{\ThCS@blk@and#2}%
    \ifnewaffil\gdef\ThCS@las{}\gdef\ThCS@lasx{}\gdef\ThCS@as{}%
        \xdef\ThCS@authors{\the\@temptokena\ThCS@blk@and}%
    \else
        \xdef\ThCS@authors{\the\@temptokena\ThCS@as\ThCS@au@str}%
        \global\let\ThCS@las\ThCS@lasx\gdef\ThCS@lasx{}%
        \gdef\ThCS@as{}%
    \fi
    \gdef\ThCS@au@str{#2}}%
        \@temptokena=\expandafter{\ThCS@authlist}%
        \let\\=\ThCSauthorcr
        \xdef\ThCS@authlist{\the\@temptokena
        \protect\@nameuse{@sep\number\c@authors}%

%  Vertical separation for author grid
%        \ifodd\value{authors}
%            \ifnum\value{authors}>1
%            \vspace*{-2em}
%            {\color{@ThCSlightred}\rule{\@ThCSauthorsrulewidth}{1pt}}
%            \protect\\
%            \vspace*{-2em}
%            \fi
%        \else
%            \ifnum\value{authors}>2
%            \vspace*{-2em}
%            \fi
%       \fi
% Vertical separation for stacked authors
   \ifnum\value{authors}>1
    \vspace*{1.5ex}
    \fi

        \protect\Authfont#2\vphantom{gy$x^{bf}$}\noexpand\ThCS@authnote{\,\ThCS@note}
        %\protect\linebreak
         %\protect\Emailfont\textcolor{@ThCSdarkred}{#3} % Original version with printed email addresses
       \Emailfont  \if&#3&{\relax}\else{\href{mailto:#3}{\color{@ThCSdarkred}\Letter}\ \ }\fi  % email icons      
       %\Orcidfont \if&#4&{\relax}\else\href{#4}{\orcidsymbol}\fi 
       \Orcidfont \if&#4&{\relax}\else{\ThCS@urlWithPrefix[https://orcid.org/]{#4}{\noexpand\orcidsymbol}}\fi 
% Horizontal Spacing for author grid
%       \ifodd\value{authors}
%            \hidden@ampersand
%        \else
%            \protect\\
%        \fi
% Stacked authors 
     \relax

        }%
    \endgroup
    \ifnum\value{authors}>1\relax
    \@namedef{@sep\number\c@authors}{}\fi
    \newaffilfalse
}

\newcommand\ThCS@urlWithPrefix[3][1]{%
	\ifblank{#2}{%
		% if author orcid not specified
		% then don't add hyperlink
	}{%
		% if author orcid specified
		\IfBeginWith{#2}{#1}%
			{\href{#2}{#3}}% use complete URL
			{\href{#1#2}{#3}}% add URL prefix
	}
}

\newcommand\ThCSauthorcr{\protect\\ \protect\Authfont \protect\ThCS@setsep}%
\newcommand\ThCSaffil[2][]%
{\newaffiltrue\let\ThCS@blk@and\ThCS@pand
    \if\relax#1\relax\def\ThCS@note{\ThCS@thenote}\else\def\ThCS@note{\csuse{note#1}}%
        \setcounter{Maxaffil}{0}\fi
    \begingroup
        \let\protect\@unexpandable@protect
        \def\thanks{\protect\thanks}\def\footnote{\protect\footnote}%
        \@temptokena=\expandafter{\ThCS@authors}%
        {\def\\{\protect\\}\xdef\ThCS@temp{#2}}%
        \xdef\ThCS@authors{\the\@temptokena\ThCS@las\ThCS@au@str
        \protect\\[\affilsep]\ThCS@temp}%
        \gdef\ThCS@las{}\gdef\ThCS@au@str{}%
        {\def\\{, \ignorespaces}\xdef\ThCS@temp{#2}}%
        \@temptokena=\expandafter{\ThCS@affillist}%
        \xdef\ThCS@affillist{\the\@temptokena
        \ThCS@affilnote{\ThCS@note}~\ThCS@temp \ThCS@affilsep}%
    \endgroup
}
%New command by Miguel
\def\@author{}
% Removed.  Does not appear to be used but causes metadata warnings.
%\renewcommand\@author{\ifx\ThCS@affillist\ThCS@empty\ThCS@author\else
%      \ifnum\value{affil}>\value{Maxaffil}\def\rlap##1{##1}%
%    \noexpand\ThCS@authlist\\[\affilsep]\noexpand\ThCS@affillist
%    \else  \ThCS@authors\fi\fi}

\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\fancypagestyle{plain}{%
    \setlength{\headheight}{32pt}%
    \fancyheadoffset[L]{64pt}%
    \fancyhead[L]{%
        \makebox[64pt]{%
        {\fontsize{14.4}{12}\selectfont \textcolor{@ThCSlightred}{\sffamily\bfseries\thepage}}{\sffamily\fontsize{10}{12}\selectfont \textcolor{@ThCSdarkred}{\hspace*{2mm}/\hspace*{2mm}\pageref{VeryLastPage}}}\hfill}%
         {\fontsize{16}{12}\selectfont \textcolor{@ThCSlightred}{\textls*{\interextrabold \if@ThCSyear \@ThCSyear \else XXXX\fi:\if@ThCSarticlenum \@ThCSarticlenum \else XX \fi}}}%
    }%
    \fancyhead[R]{%
                \@ThCSfrontlogo
    }
    

    \fancyfoot[L]{%
        \ifThCSciteas{%
        \begin{minipage}[t]{\@ThCSfirstcolwidth}%
        \sffamily\fontsize{10}{12}\selectfont\raggedright%
           \sffamily\fontsize{10}{12}\selectfont
           \color{@ThCSdarkred}%
       {\raggedright \textbf{Cite as } \ThCS@footauthors.
        \@ThCStitle.
        TheoretiCS,~Volume 
         % \if@ThCSyear {\inteval{\@ThCSyear - 2021}}
       % \else X \fi ({\if@ThCSyear \@ThCSyear\else XXXX\fi}),
       \@ThCSvolume ({\if@ThCSyear \@ThCSyear\else XXXX\fi}),     
        Article \if@ThCSarticlenum\@ThCSarticlenum \else X\fi,
        1-\pageref{VeryLastPage}.}%
        \end{minipage}}\fi
%%% Removed because it does not work and should be at the end.
        %%%% Adding pdf metadata to the paper
        %%%\hypersetup{
        %%% pdftitle=\@ThCStitle,
%%%% pdfsubject={Theoretical Computer Science}, % Not necessary
     %%%    pdfauthor=\ThCS@footauthors,
%%%%pdfkeywords={\ignorespaces\ThCSkeywords}% Removed because it doesn't work
 %%%       }
    }
    \fancyfoot[R]{%
        \begin{minipage}[t]{\@ThCSsecondcolwidth}%
        \sffamily\fontsize{10}{12}\selectfont\arraybackslash
           \color{@ThCSdarkred}%
           \hfill{https://theoretics.episciences.org}
           \linebreak
        % Automatically generated DOI
          \ifThCSdoicreated{%
            \if@ThCSyear{
            \if@ThCSarticlenum{
            \def\@ThCSdoi{10.46298/theoretics.\StrGobbleLeft{\@ThCSyear}{2}.\@ThCSarticlenum}
            \hfill\textbf{DOI} \@ThCSdoi%
             }\fi}\fi%
        }
         \else
        {\if@ThCSdoi%  Backwards compatibility for deprecated author generated DOI
        \hfill\textbf{DOI} \@ThCSdoi%
        \fi}
        \fi%
        \end{minipage}%
    }
}

\fancyheadoffset[L]{64pt}
\fancyhead[L]{%
    \makebox[64pt]{%
    {\sffamily\fontsize{14.4}{12}\selectfont \textcolor{@ThCSlightred}{\sffamily\bfseries\thepage}}{\sffamily\fontsize{12}{12}\selectfont \textcolor{@ThCSdarkred}{\hspace*{2mm}/\hspace*{2mm}\pageref{VeryLastPage}}}\hfill}%
    {\@ThCSheadlogo}%  
}


% Right-justified author and paper titles 
\fancyhead[R]{%
{%\intersemibold\fontsize{12}{12}\selectfont
\sffamily\fontsize{12}{16}\selectfont
\textcolor{@ThCSdarkred}{%
    \ifnumodd{\value{page}}{%
        \if@ThCSshorttitle
           {\@ThCSshorttitle}
        \fi
    }{%
        \if@ThCSshortnames
            {\@ThCSshortnames}
        \fi
    }
    }\hskip -10pt}
}



% Figures
\RequirePackage{floatrow}
\RequirePackage{caption}
\RequirePackage{placeins} %  Paul Added at Thomas' suggestion to define \FloatBarrier to avoid floats migrating to the end of the document.
\renewcommand{\topfraction}{0.9}	% max fraction of floats at top
\renewcommand{\bottomfraction}{0.8}	% max fraction of floats at bottom
\renewcommand{\floatpagefraction}{0.7}	
\newcounter{myfigureid}
\captionsetup{labelsep=period}
\captionsetup{justification=raggedright}
%\DeclareCaptionFormat{plain}{\sffamily\mathversion{sansmath}\fontsize{12}{18}\selectfont\color{@ThCSdarkred}\textbf{#1#2}\hspace*{6pt}#3\par}   Original version from Miguel
\DeclareCaptionFormat{plain}{{\sffamily\mathversion{sansmath}\fontsize{12}{18}\selectfont\color{@ThCSdarkred}\textbf{#1#2}}\hspace*{6pt}\sffamily\mathversion{sansmath}\fontsize{12}{18}\selectfont #3\par}%
\DeclareFloatVCode{redruleabove}%
{\refstepcounter{myfigureid}%
\zsaveposy{\themyfigureid}%
\ifnum \zposy{\themyfigureid}<60817408%
{\color{@ThCSlightred}\par\rule{\textwidth}{3pt}\vskip12pt\par}%
\fi%
}%

% Deprecated rule for side caption figures.
%\DeclareFloatVCode{redruleabovesc}%
%{\refstepcounter{myfigureid}%
%\zsaveposy{\themyfigureid}%
%\ifnum \zposy{\themyfigureid}<60817408%   Miguel's test to see if figure is not at the top of a page
%{\color{@ThCSlightred}\par\rule{\@ThCSfirstcolwidth}{3pt}\hskip32pt\rule{\@ThCSsecondcolwidth}{3pt}\vskip12pt\par}%
%\fi%
%}%
%  Paul Added redrulebelow copied from redruleabove
\DeclareFloatVCode{redrulebelow}%
{\refstepcounter{myfigureid}%
\zsaveposy{\themyfigureid}%
\ifnum \zposy{\themyfigureid}<60817408%
{\vskip12pt\color{@ThCSlightred}\par\rule{\textwidth}{3pt}\par}%
\fi%
}%
%\floatsetup[figure]{rowprecode=redruleabove}%  Original from Miguel
\floatsetup[figure]{rowprecode=redruleabove,rowpostcode=redrulebelow}%
%\floatsetup[widefigure]{rowprecode=redruleabove,capposition=beside,capbesideposition={center,right},floatwidth=\@ThCSfirstcolwidth,capbesidewidth=\@ThCSsecondcolwidth}%  Original from Miguel
% Paul's version that includes bottom rule and raggedright margin to make sure figure is left-justified and a proper separator between figure and caption.  Also, use of sidefigure instead of figure*.
\DeclareFloatSeparators{sidecaptionsep}{\hskip 32pt}
\DeclareNewFloatType{sidefigure}{name=Figure}
\floatsetup[sidefigure]{rowprecode=redruleabove,capposition=beside,capbesideposition={center,right},floatwidth=\@ThCSfirstcolwidth,capbesidewidth=\@ThCSsecondcolwidth,margins=raggedright,capbesidesep=sidecaptionsep,rowpostcode=redrulebelow}%
% Continuation figures based on Thomas's suggestion
\DeclareNewFloatType{cfigure}{name=Figure}
\floatsetup[cfigure]{rowpostcode=redrulebelow}%
\DeclareNewFloatType{csidefigure}{name=Figure}
\floatsetup[csidefigure]{capposition=beside,capbesideposition={center,right},floatwidth=\@ThCSfirstcolwidth,capbesidewidth=\@ThCSsecondcolwidth,margins=raggedright,capbesidesep=sidecaptionsep,rowpostcode=redrulebelow}%
\AtBeginEnvironment{figure}{\stepcounter{cfigure}\stepcounter{sidefigure}\stepcounter{csidefigure}}
\AtBeginEnvironment{cfigure}{\stepcounter{figure}\stepcounter{sidefigure}\stepcounter{csidefigure}}
\AtBeginEnvironment{csidefigure}{\stepcounter{figure}\stepcounter{sidefigure}\stepcounter{cfigure}}
\AtBeginEnvironment{sidefigure}{\stepcounter{figure}\stepcounter{cfigure} \stepcounter{csidefigure}}

% scaling factors for use with figures
\newcommand{\ThCSscalefactor}{1.288}
\newlength{\ThCScm}
\setlength{\ThCScm}{\ThCSscalefactor cm}
\newlength{\ThCSpt}
\setlength{\ThCSpt}{\ThCSscalefactor pt}
\newlength{\ThCSin}
\setlength{\ThCSin}{\ThCSscalefactor in}

\newcommand{\ThCStikzlinewidths}{
\tikzset{ultra thin/.style=              {line width=0.2pt}}%
\tikzset{very thin/.style=               {line width=0.4pt}}%
\tikzset{thin/.style=                    {line width=0.8pt}}%
\tikzset{semithick/.style=               {line width=1.2pt}}%
\tikzset{thick/.style=                   {line width=1.6pt}}%
\tikzset{very thick/.style=              {line width=2.4pt}}%
\tikzset{ultra thick/.style=             {line width=3.2pt}}%
}

% Algorithms
\RequirePackage[linesnumbered,noline,noend,noresetcount]{algorithm2e}
\setlength\algomargin{32pt}
\SetKwComment{tcc}{$>$~}{}%
\SetKwComment{tcp}{$>$~}{}%
\renewcommand\AlCapSty{\textbf}
\renewcommand\AlCapFnt{\sffamily\fontsize{12}{18}\selectfont\color{@ThCSdarkred}}
\renewcommand\AlCapNameSty{\textnormal}
%\renewcommand\AlCapNameFnt{\sffamily\fontsize{12}{18}\selectfont\color{@ThCSdarkred}}% Original from Miguel
\renewcommand\AlCapNameFnt{\sffamily\fontsize{12}{18}\selectfont}
\SetAlgoCaptionSeparator{.}
\SetAlgoCaptionLayout{raggedright}
\DontPrintSemicolon
\SetAlFnt{\mathversion{sansmath}\fontsize{14.4}{20}\selectfont\ttfamily}
%\SetAlFnt{\mathversion{sansmath}\fontsize{14.4}{20}\selectfont}
\setlength\algomargin{60pt}
\SetInd{32pt}{0pt}
\SetKwProg{Fn}{function}{}{}
\SetNlSkip{28pt}
\SetAlCapSkip{1em}
\renewcommand{\KwSty}[1]{\textbf{\texttt{#1}}\unskip}%
\renewcommand{\FuncArgSty}[1]{\texttt{#1}\unskip}%
\renewcommand{\ArgSty}[1]{\texttt{#1}\unskip}%
\renewcommand{\NlSty}[1]{\fontsize{10}{10}\selectfont\texttt{\textcolor{@ThCSdarkred}{#1:}}\unskip}%

\renewcommand{\CommentSty}[1]{\sffamily\fontsize{10}{12}\selectfont\textcolor{@ThCSdarkred}{#1}\unskip}%

\pretocmd{\@algocf@start}{
    \vspace*{12pt}
    \noindent{\color{@ThCSlightred}\rule{\textwidth}{3pt}}
}{}{}

% Added by Paul copied from Miguel's code to add red rule above algorithms to put rule at the end of algorithms which patches an internal command from the algorithm2e package.
\apptocmd{\@algocf@finish}{
    \vspace*{12pt}
    \noindent{\color{@ThCSlightred}\rule{\textwidth}{3pt}}
    \vspace*{12pt}
}{}{}

\renewcommand{\algocf@makecaption}[2]{%
  \addtolength{\hsize}{\algomargin}%
  \sbox\@tempboxa{\algocf@captiontext{#1}{#2}}%
  \parbox[t]{\hsize}{\algocf@captiontext{#1}{#2}}%
  \addtolength{\hsize}{-\algomargin}%
}%

\renewcommand{\algocf@printnl}[1]{%
  \ifthenelse{\boolean{algocf@leftlinenumber}}{%
    \skiplinenumber=\skiptotal\advance\skiplinenumber by\leftskip%
    \strut\raisebox{0pt}{\llap{\NlSty{#1}\kern\skiplinenumber}}\ignorespaces%
  }
}%

% Bibliography/references
\RequirePackage{multicol}

\RequirePackage[style=trad-plain,backend=biber,locallabelwidth=true,natbib=true,url=true,doi=true,isbn=false,maxbibnames=99,backref=true,backrefstyle=three,autopunct=false]{biblatex}
%\{english}{%
%  backrefpage = {p.},% originally "cited on page"
%  backrefpages = {pp.},% originally "cited on pages"
%}
\DeclareSourcemap{
  \maps[datatype=bibtex]{
    \map{
      \step[fieldsource=url,
        match=\regexp{\\_},
        replace=\regexp{_}]
    }
  }
}
\DeclareSourcemap{
  \maps[datatype=bibtex]{
    \map{
      \step[fieldsource=doi,
        match=\regexp{\\_},
        replace=\regexp{_}]
    }
  }
}
\renewbibmacro*{pageref}{\color{@ThCSdarkred}{\iflistundef{pageref}{}{\printtext[parens]{\printlist[‌​pageref][-\value{listtotal}]{pageref}}}}}
% move period from end to after year
\renewcommand{\finentrypunct}{}
\renewbibmacro*{date}{\printdate\adddot}
\renewbibmacro*{doi+eprint+url}{%
  %\setunit{\addspace}\newblock
  %%% Swap order of note and DOI
  \newunit\newblock%
  \printfield{note}%
  \setunit{\adddot\addspace}\newblock%
 \iftoggle{bbx:doi}
   {\printfield{doi}}
   {}
 % \newunit\newblock
 % \iftoggle{bbx:eprint}
 %   {\usebibmacro{eprint}}
 %   {}%
 \ifboolexpr{
togl {bbx:url} and ((not togl {bbx:doi}) or test {\iffieldundef{doi}} )
}
{\usebibmacro{url}}
{}
 \ifboolexpr{ togl {bbx:eprint} and 
 (not test {\iffieldundef{eprinttype}}) and 
 (test {\iffieldequalstr{eprinttype}{extra-open}}) and
 (togl {bbx:doi} and (not test {\iffieldundef{doi}} ) )
}
{\usebibmacro{eprint}}
{}
% part of swapping the order of note and DOI
\clearfield{note}%
}
%\DeclareFieldFormat{doi}{\href{https://doi.org/#1}{\color{@ThCSdarkred}\framebox{\sffamily\fontsize{8}{12}\selectfont DOI}}}
\DeclareFieldFormat{doi}{\href{https://doi.org/#1}{
  \colorbox{gray}{\textcolor{white}{\sffamily\fontsize{8}{12}\selectfont DOI}}}} 
\DeclareFieldFormat{url}{\href{#1}{
  %\color{@ThCSdarkred}\framebox{\sffamily\fontsize{8}{12}\selectfont URL}
  \colorbox{gray}{\textcolor{white}{\sffamily\fontsize{8}{12}\selectfont URL}}  
}}
\DeclareFieldFormat{eprint:extra-open}{\href{#1}{%
  \colorbox{gray}{\textcolor{white}{\sffamily\fontsize{8}{12}\selectfont ePrint}}  
}}
\AtEveryBibitem{%
\ifentrytype{inproceedings}{% Remove editors for proceedings
    \clearname{editor}
   % \clearlist{publisher}
    }{}
}

\setlength{\biblabelsep}{\labelsep}%
\defbibenvironment{bibliography}
  {\list
     {\printtext[labelnumberwidth]{%
        \printfield{labelnumber}%
     }}
     {\setlength{\labelsep}{\biblabelsep}%
      \setlength{\leftmargin}{32pt}%
      \setlength{\itemsep}{\bibitemsep}%
      \setlength{\parsep}{\bibparsep}}%
  \renewcommand*{\makelabel}[1]{\hss\hspace*{-8pt}##1}}
  {\endlist}
  {\item}

\renewcommand*{\bibfont}{\sffamily\fontsize{10}{12}\selectfont}
%\renewcommand*{\citesetup}{%
%    \intersemibold\fontsize{12}{12}\selectfont\color{@ThCSdarkred}
%    \biburlsetup
%    \frenchspacing}%Original from Miguel
\newlength{\@currfontsize}
\newcommand{\citefont}{%
\setlength{\@currfontsize}{\f@size pt}%
\ifdim\@currfontsize<12.0pt%
         \intersemibold\fontsize{10}{12}\selectfont%
     \else 
         \intersemibold\fontsize{12}{12}\selectfont%
     \fi
     }
\renewcommand*{\citesetup}{%
    %\citefont
    \color{@ThCSdarkred}
    \biburlsetup
    \frenchspacing}

% Paul modified version of textcite from biblatex/cbx/numeric.cbx to make colors switch to black for names.
\renewbibmacro*{textcite}{%
  \iffieldequals{namehash}{\cbx@lasthash}
    {\setunit{\multicitedelim}}
    {\ifnameundef{labelname}
       {\printfield[citetitle]{labeltitle}}
       %Switch colors before and after names
       {\normalfont\color{black}\printnames{labelname}\color{@ThCSdarkred}}\citefont%
     \setunit*{\printdelim{namelabeldelim}}%
     \printtext{\bibopenbracket}\global\booltrue{cbx:parens}%
     \stepcounter{textcitecount}%
     \savefield{namehash}{\cbx@lasthash}}%
  \ifnumequal{\value{citecount}}{1}
    {\usebibmacro{prenote}}
    {}%
  \usebibmacro{cite}%
  \setunit{%
    \ifbool{cbx:parens}
      {\bibclosebracket\global\boolfalse{cbx:parens}}
      {}%
    \textcitedelim}}

\renewbibmacro*{cite}{%
  \citefont
  \printtext[bibhyperref]{%
    \printfield{labelprefix}%
    \printfield{labelnumber}%
    \ifbool{bbx:subentry}
      {\printfield{entrysetcount}}
      {}}}

\AtBeginBibliography{
\DeclareFieldFormat*{labelnumber}{\thefield{labelnumber}}
\DeclareFieldFormat*{labelnumberwidth}{\intersemibold\fontsize{12}{12}\selectfont\textcolor{@ThCSdarkred}{[#1]}}
\DeclareFieldFormat*{extraalpha}{}
\renewcommand*{\mkbibnamegiven}[1]{\intersemibold #1}%
\renewcommand*{\mkbibnamefamily}[1]{\intersemibold #1}%
\renewcommand*{\mkbibnameprefix}[1]{\intersemibold #1}%
\renewcommand*{\mkbibnamesuffix}[1]{\intersemibold #1}%
%\renewcommand*{\finalnamedelim}{\addspace\intersemibold and\addspace}%  Original from Miguel
\renewcommand*{\finalnamedelim}{ \ifnumgreater{\value{liststop}}{2}{\finalandcomma}{}\addspace\intersemibold and\addspace}% Replacement by Paul to add comma before final "and" in lists of 3 or more authors.
%\DeclareFieldFormat*{title}{\itshape #1}% Original from Miguel
\DeclareFieldFormat*{title}{\intermedium #1}
\DeclareFieldFormat*{booktitle}{\itshape {#1}} % Added by Paul
%\DeclareFieldFormat*{journaltitle}{ #1}% Original from Miguel
\DeclareFieldFormat*{journaltitle}{\itshape {#1}}
\renewbibmacro{in:}{}
}

% Added by Paul to prevent bibliography entries splitting across columns or pages.
\patchcmd{\thebibliography}{\clubpenalty4000}{\clubpenalty10000}{}{}     % no orphans
\patchcmd{\thebibliography}{\widowpenalty4000}{\widowpenalty10000}{}{}   % no widows
\patchcmd{\bibsetup}{\interlinepenalty=5000}{\interlinepenalty=10000}{}{} % no break of entry

\let\oldprintbibliography\printbibliography
\def\printbibliography{
    \zsaveposy{posrefstart}
    \ifnum \zposy{posrefstart}<60817408%
    {\vspace*{12pt}
    \noindent{\color{@ThCSlightred}\rule{\textwidth}{3pt}}%
    \vspace*{-12pt}}\fi
    \phantomsection
    \section*{References}
    \addcontentsline{toc}{section}{References}
    \begingroup
    \vspace*{-24pt}
    \setlength\columnsep{32pt}
    \begin{multicols}{2}
    \raggedcolumns
    \raggedright\oldprintbibliography[heading=none]
    \end{multicols}
    \endgroup
}

% Redeclare \maketitle
\renewcommand\maketitle{
\newpage
\thispagestyle{plain}
\null

% Moved from front of abstract
\if@ThCSthanks{{\let\thefootnote\relax\footnote{\hspace{-32pt}\parbox[t]{\dimexpr\@ThCSfirstcolwidth+\@ThCSsecondcolwidth+32pt}%
{\@ThCSthanks}}}%
\setcounter{footnote}{0}}\fi

% Minipage-based title and info added by Paul
\noindent\begin{minipage}[t]{\@ThCSfirstcolwidth}
\@HY\raggedright\arraybackslash \sffamily
\expandarg\StrLen{\@title}[\@titlelen]
\ifnum\@titlelen<80
    \setlength{\baselineskip}{40pt}
    \fontsize{30pt}{24pt}
\else
    \setlength{\baselineskip}{36pt}
    \fontsize{24pt}{24pt}
\fi
\vskip -12pt  %Extra skip so title and side bar align.   Has net effect of raising side-bar.
{\mathversion{sansmath}\selectfont\intermedium\@title}
\end{minipage}%
\hskip 32pt
\begin{minipage}[t]{\@ThCSsecondcolwidth}
%\vskip -\titlebaseline
\@HY\raggedright\arraybackslash
\sffamily\fontsize{10pt}{12pt}\selectfont
\textcolor{@ThCSdarkred}{
\if@ThCSreceived
    \textbf{Received}
    \@ThCSreceived \linebreak
\fi
\if@ThCSrevised
    \textbf{Revised}
    \@ThCSrevised \linebreak
\fi
\if@ThCSaccepted
    \textbf{Accepted}
    \@ThCSaccepted \linebreak
\fi
\if@ThCSpublished
    \textbf{Published}
    \@ThCSpublished \linebreak
\fi
\if@ThCSupdated
    \textbf{Updated}
    \@ThCSupdated \linebreak
\fi
\if@ThCSlinebreak
    \linebreak
\fi
\if@ThCSkeywords
    \textbf{Key words and phrases} \linebreak
    \@ThCSkeywords  
\fi
}
\end{minipage}

%\vspace*{36pt}% original from Miguel
\vspace*{12pt}%  Modified by Paul

\noindent\begin{tabularx}{\textwidth}{@{}R@{\hskip 32pt}Z@{}}
%{\vspace*{-1em}\color{@ThCSlightred}\rule{\@ThCSfirstcolwidth}{3pt}\vspace*{.6em}}
{\vspace*{-1em}\color{@ThCSlightred}\rule{\@ThCSfirstcolwidth}{3pt}\vspace*{24pt}}
%{\begin{tabularx}{\textwidth}{@{}@{\hskip 32pt}QQ@{}}% Original from Miguel which indents authors according to style.
%{\begin{tabularx}{\@ThCSfirstcolwidth}{@{}@{\hskip 32pt}QQ@{}}% modification by Paul which sets authors in table of width of 1st column rather than all of \textwidth
%{\begin{tabularx}{\@ThCSfirstcolwidth}{@{}Q@{\hskip 16pt}Q@{}}% modification by Paul which eliminates the indent and sets authors in table of width of 1st column rather than all of \textwidth
 % No tabular layout stacked authors
\if@authorindent
{\begin{tabularx}{\@ThCSfirstcolwidth}
{@{}@{\hskip 32pt}Q@{}}
\ThCS@authlist
\end{tabularx}}
\else
{\begin{tabularx}{\@ThCSfirstcolwidth}{@{}Q@{\hskip 32pt}@{}}
\ThCS@authlist
\end{tabularx}}
\fi

&
%{\vspace*{-1em}\color{@ThCSlightred}\rule{\@ThCSsecondcolwidth}{3pt}\vspace*{.6em}}
{\vspace*{-1em}\color{@ThCSlightred}\rule{\@ThCSsecondcolwidth}{3pt}\vspace*{24pt}}
{\fontsize{10pt}{12pt}
\textcolor{@ThCSdarkred}{
\sffamily
\ThCS@affillist
}
} \\
\end{tabularx}

\global\let\thanks\relax
\global\let\maketitle\relax
\global\let\@maketitle\relax
\global\let\@thanks\@empty
\global\let\@ThCSauthor\@empty
\global\let\@date\@empty
\global\let\@title\@empty
\global\let\@ThCSreceived\@empty
\global\let\@ThCSrevised\@empty
\global\let\@ThCSaccepted\@empty
\global\let\@ThCSpublished\@empty
\global\let\@ThCSupdated\@empty
\global\let\@ThCSkeywords\@empty
\global\let\title\relax
\global\let\ThCSauthor\relax
\global\let\date\relax
\global\let\and\relax
\global\let\ThCSreceived\relax
\global\let\ThCSrevised\relax
\global\let\ThCSpublished\relax
\global\let\ThCSupdated\relax
\global\let\ThCSkeywords\relax
\global\let\ThCSdoi\relax
}


% Now loaded last
\RequirePackage[hidelinks,hypertexnames=false]{hyperref}
% load to enable metadata
\RequirePackage{hyperxmp}

% META DATA
\newcommand{\@ThCS@setupMetadataViaHyperxmp}{%
    \hypersetup{%
        pdftitle=\@ThCStitle,
        pdfauthor=\ThCS@footauthors,
        pdfdoi={\if@ThCSdoi\@ThCSdoi\fi},
        pdfkeywords={\if@ThCSkeywords\@ThCSkeywords\fi},
        pdfcopyright=\ThCS@footauthors,
        pdflicenseurl={https://creativecommons.org/licenses/by/4.0/},
        pdfproducer={pdfLaTeX with theoretics.cls v\@ThCSversionnum},
        pdflang={en},
        pdfmetalang={en},
        pdfpublisher={TheoretiCS Foundation},
        pdfvolumenum={\@ThCSvolume},
        pdfissuenum={\if@ThCSarticlenum \@ThCSarticlenum \else XX \fi},
    }%
}

\AtEndPreamble{\@ThCS@setupMetadataViaHyperxmp}



\endinput
