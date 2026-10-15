%% Public latex class for AlCo
\NeedsTeXFormat{LaTeX2e}% LaTeX 2.09 can't be used (nor non-LaTeX)
[1995/06/01]% LaTeX date must be June 1995 or later
\ProvidesClass{cedram-alco}[2017/11/22 v0.2]
\DeclareOption{Unicode}{\relax}
\ProcessOptions\relax
%% Loading amsart
\LoadClass[centertags,portrait,10pt,twoside,%
 onecolumn]{amsart}[2004/08/06 v2.20]
%% Modifs amsart for cedram  compatibility
\AtBeginDocument{%
  \@for\@tempa:=-1,0,1,2,3,4\do{%
    \@ifundefined{r@tocindent\@tempa}{%
      \@xp\gdef\csname r@tocindent\@tempa\endcsname{0pt}}{}%
  }%
}
\def\@writetocindents{%
  \begingroup
  \@for\@tempa:=-1,0,1,2,3\do{%
    \immediate\write\@auxout{%
      \string\newlabel{tocindent\@tempa}{%
        \csname r@tocindent\@tempa\endcsname}}%
  }%
  \endgroup}

\RequirePackage[english]{isodate}
\RequirePackage{mathtools}
\RequirePackage[shortlabels]{enumitem}
\setlist{font=\upshape}
%% Cedram structure for \author
\renewcommand{\author}[2][]{%
  \ifx\@empty\authors
    \gdef\authors{#2}%
    \g@addto@macro\addresses{\author{#2}}%
  \else
    \g@addto@macro\authors{\and#2}%
    \g@addto@macro\addresses{\author{#2}}%
  \fi
  \@ifnotempty{#1}{%
    \ifx\@empty\shortauthors
      \gdef\shortauthors{#1}%
    \else
      \g@addto@macro\shortauthors{\and#1}%
    \fi
  }%
}
\edef\author{\@nx\@dblarg
  \@xp\@nx\csname\string\author\endcsname}
%% Metadata
% journal title
\newcommand{\setpublname}[2][]{%
\gdef\shortpublname{#1}\gdef\publname{#2}}
\setpublname[Alg. Comb.]{Algebraic Combinatorics}%
\def\currentjournaltitle{Algebraic Combinatorics}%
% journal publisher
\edef\currentjournalpublisher{MathOA foundation}
% journal short title
\def\currentjournalshorttitle{Alg. Comb.}%
% acronym
\def\cdr@journalacro{ALCO}
% ISSN (electronic)
\def\@Eissn{2589-5486}
%% URL
\def\journalURL{http://algebraic-combinatorics.org/}

%% article metadata
\let\@altabstract\@empty
\let\@alttitle\@empty
\newcommand*{\alttitle}[1]{\gdef\@alttitle{#1}}%
\newcommand*{\altkeywords}[1]{\gdef\@altkeywords{#1}}%
\newbox\altabstractbox
\newenvironment{altabstract}{%
  \ifx\maketitle\relax
    \ClassWarning{\@classname}{Altabstract should precede
      \protect\maketitle\space in AMS document classes; reported}%
  \fi
  \global\setbox\altabstractbox=\vtop \bgroup
    \normalfont\Small
    \list{}{\labelwidth\z@
      \leftmargin3pc \rightmargin\leftmargin
      \listparindent\normalparindent \itemindent\z@
      \parsep\z@ \@plus\p@
      \let\fullwidthdisplay\relax
    }%
    \item[\hskip\labelsep\scshape\altabstractname.]%
}{%
  \endlist\egroup
  \ifx\@setaltabstract\relax \@setaltabstracta \fi
}
\def\@setaltabstract{\@setaltabstracta \global\let\@setaltabstract\relax}
\def\@setaltabstracta{%
\ifx\@empty\@alttitle\else
\begin{center}%
\large\itshape  \@alttitle  
\end{center}%
\fi
  \ifvoid\altabstractbox
  \else
    \box\altabstractbox
    \prevdepth\z@ % because \altabstractbox is a vtop
  \fi
}
\def\@setabstract{\@setabstracta \global\let\@setabstract\relax
\@setaltabstract}
%% geometry A4/letter compatible, defined as A4
\paperwidth=201mm
\paperheight=297mm
\textwidth=130truemm
\textheight=230truemm
\ifx\undefined\pdfpagewidth\else
\pdfpagewidth\paperwidth
\pdfpageheight\paperheight
\fi
\headheight=10pt
\headsep 10mm
\footskip 10mm 
\columnsep=10pt \columnseprule=0pt
\marginparsep=10pt
\marginparpush=5pt
\marginparwidth=65pt
\skip\footins=12pt plus12pt
\skip\@mpfootins=\skip\footins

\calclayout

\voffset-.5truecm
%%
\normalparindent=12pt
\parindent=\normalparindent
\frenchspacing
%
%
\let\@listI\@listi
\@listi

%% Fonts
\def\@captionheadfont{\scshape}%

%% Page layout
%% 1st page
\pagenumbering{arabic}%
%%  Copyright
\def\@setcopyright{}%
%% Page style 
\def\ps@firstpage{%
  \ps@plain
  \def\@oddfoot{{\scriptsize    
      ISSN\string: \@Eissn\hfill\url{\journalURL}
}}
  \let\@evenfoot\@oddfoot
  \def\@oddhead{\@serieslogo\hss}%
  \let\@evenhead\@oddhead % in case an article starts on a left-hand page
}
%
%% Identificiation article 1st page
\def\pageinfosep{--}
\def\@logofont{\footnotesize}
\def\article@logo{%
  \set@logo{%
    \textit{\currentjournaltitle}\\
    \textbf{Draft} 
  }%
}
%
%%  Copyright
\def\@setcopyright{}%
%% Standard pages
\def\ps@headings{\ps@empty
  \def\@evenhead{%
    \setTrue{runhead}%
    \scshape\footnotesize\def\lastname####1{\textsc{####1}}%
%    \rlap{\thepage}
    \hfil
    \def\thanks{\protect\thanks@warning}%
    \leftmark{}{}\hfil}%
  \def\@oddhead{%
    \setTrue{runhead}%
    \itshape\footnotesize
    \hfil
    \def\thanks{\protect\thanks@warning}%
    \rightmark{}{}\hfil
    % \llap{\thepage}
  }%
  \def\@oddfoot{%
    \rlap{\scriptsize\textit{\currentjournaltitle}, draft (\today)}\hfil\thepage
    }%
  \let\@evenfoot\@oddfoot
}
\pagestyle{headings}%
%%  Title presentation 
\def\@settitle{%
 \vtop to 40 mm{%
   \begin{center}\vspace*{-1cm}
  \def\baselinestretch{1.2}\large\vfil
    {\Huge\@title\par}
  \vfil\vfil
  \begin{minipage}{.8\textwidth}\centering
   {\cdr@authorfont \edef\cdrandname{{\noexpand\cdr@andfont
          \cdrandname}} \andify\authors\authors\par}
  \end{minipage}
  \end{center}}%
 \par\bigskip
}
\def\cdr@byfont{\normalfont}
\def\cdr@authorfont{\normalfont\large}
\def\cdr@andfont{\normalfont}
%% Pr\'esentation des auteurs
  \def\cdrbyname{by}%
  \def\manuscriptname{Manuscript}%
  \def\receivedname{received}%
  \def\revisedname{revised}%
  \def\acceptedname{accepted}%
  \def\@@and{\&}%
  \def\cdrandname{\&}%
  \def\@setauthors{}%
%% abstracts presentation
  \def\abstractheadfont{\scshape}
\def\alttitlefont{\normalfont}
\def\@setabstracthead{{\abstractheadfont\abstractname}}
\def\@setaltabstracthead{{\abstractheadfont
  \altabstractname}%
 \ifx\@alttitle\@empty\else\ {\alttitlefont\textup(\@alttitle\textup)}\fi}

%% Footnotes 1st page
\def\@adminfootnotes{%
  \let\@makefnmark\relax  \let\@thefnmark\relax
  \begingroup\normalparindent0pt\footnotesep10pt\relax
  \@footnotetext{\itshape This paper has been prepared using ALCO author class
    on \today.}
  \ifx\@empty\@keywords\else \@footnotetext{\parindent\z@\@setkeywords}\fi
  \ifx\@empty\thankses\else \def\par{\let\par\@par}\@footnotetext{\parindent\z@\@setthanks}%
  \fi
\endgroup}
%
\def\dedicatoryfont{\normalfont\footnotesize\itshape}
\def\@setdedicatory{%
    \begingroup
      \def\signature##1{\nobreak\hskip 2em plus 1fil
        \penalty-5\hbox{}\nobreak\hfil\parfillskip=0pt
        \mbox{\upshape ##1}\par}
      \raggedleft
      \dedicatoryfont
      \@dedicatory\par
    \endgroup}
\def\@setkeywords{%
  \footnotesize\hskip-\normalparindent
  {\abstractheadfont\keywordsname.}\enspace\ignorespaces
  \@keywords\@addpunct{{\upshape.}}}
\newcount\CDR@numberofthanks\CDR@numberofthanks=0\relax
\def\@setthanks{\footnotesize\hskip-\normalparindent\def\thanks##1{\ifnum\CDR@numberofthanks=0\relax\else\@par\fi##1\@addpunct{{\upshape.}}\advance\CDR@numberofthanks1\relax}{\abstractheadfont\thanksname.}\enspace\ignorespaces\thankses}
\def\@settranslators{\par
  \begingroup
  \translatedby\ \andify\@translators
  {\sl \ignorespaces\@translators} \@@par
  \endgroup}
 \def\keywordsname{Keywords}
 \def\subjclassname{Mathematical subject classification (2010)}
 \def\thanksname{Acknowledgements}
 \providecommand{\abstractname}{Abstract}
 \providecommand{\altabstractname}{R{\'e}sum{\'e}}

\@xp\let\csname subjclassname@2000\endcsname \subjclassname
\@xp\let\csname subjclassname@2010\endcsname \subjclassname
\@xp\let\csname subjclassname@2020\endcsname \subjclassname
\let\nobreakauthor~
\def\initial#1{#1}
\def\lastname#1{#1}
\def\firstname#1{#1}
\def\middlename#1{#1}
\def\vonname#1{#1}
\def\@setsubtitle{%
  \bgroup
  \centering
  \vglue-3mm
  \fontsize{12}{15}\fontseries{b}\selectfont
  %\usefont{T1}{lmr}{b}{n}%
%  \uppercasenonmath\@subtitle
  \@subtitle
  \vskip10pt plus 3pt minus 4pt
  \egroup
}
\def\@setdedicatory{%
	\vtop{\raggedleft{\footnotesize\slshape\@dedicatory\@@par}}}
%\advance\@titlebotskip-7mm
\def\cdr@preabstracthook{%
  \centerline{\vrule depth0pt height0.4pt width 1.3cm}%
}
%% Notes
\def\@makefnmark{%
  \leavevmode
	\raise.9ex\hbox{\fontsize\sf@size\z@\normalfont(\@thefnmark)\kern.15em}\ignorespaces%
}
\def\@makefntext{\noindent\@makefnmark}
%
\AtBeginDocument{%
  \@ifpackageloaded{hyperref}{}{\def\href#1#2{#2}}%
  \@ifpackageloaded{url}{}{\def\url#1{#1}}%
  }
\def\longthankssection{\subsubsection*{Acknowledgements}}
  \long\def\longthanks#1{\longthankssection

  #1}
%%% Theorems
\RequirePackage{amsthm,amssymb,upref,hyperref}
\def\th@plain{%
  \let\thm@indent\noindent
  \thm@headfont{\scshape}%
  \thm@notefont{\normalfont}%
  \thm@preskip.5\linespacing \@plus .5\linespacing
  \thm@postskip\thm@preskip
  \thm@headpunct{\MakePoint}
  \let\thmheadnl\relax
  \itshape }
\def\th@definition{\th@plain \upshape }
\def\th@remark{\th@definition }

  
%% Sectinoning
\DeclareRobustCommand{\MakePoint}{%
    \nobreak.}
\def\@seccntformat#1{%
  \protect\textup{\protect\@secnumfont
    \csname the#1\endcsname
    \protect\@secnumpunct
  }%
}
\def\@sectionfamily{\normalfont}
\def\@sectionfont{\@sectionfamily\large\scshape}
\let\contentsnamefont\@sectionfont
\def\@secnumfont{\selectfont}
\def\@upn{\normalfont\selectfont}
\def\@subsectionfont{\@sectionfamily\scshape}
\def\@subsubsectionfont{\@sectionfamily\itshape}

\newif\ifcdr@ee
\newbox\cdr@eebox
\newcount\cdr@sf
\def\@sect#1#2#3#4#5#6[#7]#8{%
  \edef\@toclevel{\ifnum#2=\@m 0\else\number#2\fi}%
  \ifnum #2>\c@secnumdepth \let\@secnumber\@empty
  \else \@xp\let\@xp\@secnumber\csname the#1\endcsname\fi
  \@tempskipa #5\relax
   \setbox\cdr@eebox\hbox{#8\global\cdr@sf\the\spacefactor}%
   \ifdim\wd\cdr@eebox>\z@\cdr@eefalse\else\cdr@eetrue\fi
  \ifnum #2>\c@secnumdepth
    \let\@svsec\@empty
  \else
    \refstepcounter{#1}%
    \edef\@secnumpunct{%
      \ifdim\@tempskipa>\z@ % not a run-in section heading
        \ifcdr@ee\else .\@nx\enspace\fi
      \else
        \ifcdr@ee \else .\@nx\enspace\fi
      \fi}%
    \ifcdr@ee
      \ifnum #2=\tw@ \def\@secnumfont{}\fi
    \fi
    \protected@edef\@svsec{%
      \ifnum#2<\@m
        \@ifundefined{#1name}{}{%
          \ignorespaces\csname #1name\endcsname\space
        }%
      \fi
      \@seccntformat{#1}%
    }%
  \fi
  \ifdim \@tempskipa>\z@ % then this is not a run-in section heading
     \begingroup #6{\relax
     \@hangfrom{\hskip #3\relax\@svsec}{\interlinepenalty\@M #8\@@par}}%
     \endgroup
    \ifnum#2>\@m \else \@tocwrite{#1}{#8}\fi
  \else
   \ifcdr@ee
     \def\@svsechd{#6{\hskip #3\@svsec\unskip}\MakePoint
                      \ifnum#2>\@m \else \@tocwrite{#1}{#8}\fi }%
  \else
     \def\@svsechd{#6{\hskip #3\@svsec\ignorespaces #8}\unskip
       \spacefactor\cdr@sf\MakePoint%
       \ifnum#2>\@m \else \@tocwrite{#1}{#8}\fi }%
  \fi
\fi
  \global\@nobreaktrue
  \@xsect{#5}}

\def\section{\@startsection{section}{1}%
  \z@{-.7\linespacing\@plus-\linespacing}{.5\linespacing}%
  {\@sectionfont\centering}}
\def\subsection{\@startsection{subsection}{2}%
  \z@{.5\linespacing\@plus.7\linespacing}{-.5em}%
  {\normalfont\@subsectionfont}}
\def\subsubsection{\@startsection{subsubsection}{3}%
  \z@{.5\linespacing\@plus.7\linespacing}{-.5em}%
  {\normalfont\@subsubsectionfont}}

\def\Subsection{\@startsection{subsection}{2}%
  \z@{.7\linespacing\@plus.7\linespacing}{.3\linespacing}
  {\normalfont\@subsectionfont}}
\def\Subsubsection{\@startsection{subsubsection}{3}%
  \z@{.4\linespacing}{.2\linespacing}%
  {\normalfont\@subsubsectionfont}}
\let\subsectionc\Subsection
\let\subsubsectionc\Subsubsection

\newcount\tochyphenpenalty
\tochyphenpenalty\@M
\def\@tocline#1#2#3#4#5#6#7{\relax
  \ifnum #1>\c@tocdepth % then omit
  \else
    \par \addpenalty\@secpenalty\addvspace{#2}%
    \begingroup \hyphenpenalty\tochyphenpenalty
    \@ifempty{#4}{%
      \@tempdima\csname r@tocindent\number#1\endcsname\relax
    }{%
      \@tempdima#4\relax
    }%
    \parindent\z@ \leftskip#3\relax
      \advance\leftskip\@tempdima\relax
    \advance\rightskip\@pnumwidth % plus1em
    \parfillskip-\@pnumwidth
    {#5{\leavevmode\hskip-\@tempdima #6}}%
    \nobreak
    \xleaders\hbox to1ex{\normalfont\hss.\hss}\hfil\nobreak
    \hbox to\@pnumwidth{\@tocpagenum{#7}}\par
    \nobreak
    \endgroup
  \fi}

\renewcommand{\tocpart}[3]{%
  \indentlabel{\@ifnotempty{#2}{\ignorespaces#1 #2.\kern1ex}}#3}
\let\tocsection\tocpart
\let\tocsubsection\tocsection
\let\tocsubsubsection\tocsection
\let\tocparagraph\tocsection
\def\l@part{\@tocline{-1}{12pt plus2pt}{0pt}{}{\bfseries\cdr@boldmath}}
\def\l@section{\@tocline{1}{0pt}{0pc}{}{}}
\def\l@subsection{\@tocline{2}{0pt}{1pc}{}{}}
\def\l@subsubsection{\@tocline{3}{0pt}{2pc}{}{}}
\def\l@paragraph{\@tocline{5}{0pt}{3pc}{}{}}
\def\l@figure{\@tocline{0}{3pt plus2pt}{0pt}{}{}}
\let\l@table\l@figure

%% Additional space tuning %%
\emergencystretch2em
\arraycolsep 1.5pt

%% predefined macros
\let\le\leqslant
\let\ge\geqslant 
\let\leq\leqslant   
\let\geq\geqslant
\let\emptyset\varnothing
\def\sfrac#1#2{{#1}/{#2}}
\def\loccit{loc.\kern3pt cit.\kern.3em}
\def\cf{cf.\kern.3em}
\def\eg{e.g.\kern.3em}
\def\ie{i.e.\kern.3em}
\def\resp{\text{resp.}\kern.3em}
\def\vs{vs.\kern.3em}
\def\etc{etc.\kern.3em}
\let\ecc\etc
\let\oldsetminus\setminus
\let\setminus\smallsetminus
\newcommand{\arXiv}[1]{\href{http://arxiv.org/abs/#1}{\texttt{arXiv\string:\allowbreak#1}}}
\newcommand{\eprinthal}[1]{\href{https://hal.archives-ouvertes.fr/hal-#1}{\texttt{hal-#1}}}
\AtEndOfClass{%
\let\oldbigoplus\bigoplus
\let\oldbigcup\bigcup
\let\oldbigcap\bigcap
\let\oldbigotimes\bigotimes
\let\oldbigwedge\bigwedge
\let\oldcoprod\coprod
}
\AtBeginDocument{%
\def\bigoplus{\mathop{\textstyle\oldbigoplus}\displaylimits}%
\def\bigcup{\mathop{\textstyle\oldbigcup}\displaylimits}%
\def\bigcap{\mathop{\textstyle\oldbigcap}\displaylimits}%
\def\bigotimes{\mathop{\textstyle\oldbigotimes}\displaylimits}%
\def\bigwedge{\mathop{\textstyle\oldbigwedge}\displaylimits}%
\def\coprod{\mathop{\textstyle\oldcoprod}\displaylimits}%
}

%% Predefined theorems
\newif\ifcdr@thmsin\cdr@thmsintrue
\newif\ifcdr@thmsas\cdr@thmsasfalse
\newif\ifcdr@thm@necounter\cdr@thm@necounterfalse
\def\OneNumberAllTheorems{\cdr@thm@necountertrue}
\OneNumberAllTheorems
\def\NumberTheoremsIn#1{\@ifempty{#1}%
     {\cdr@thmsinfalse}%
     {\@ifundefined{c@#1}{\@nocounterr{#1}}%
       {\cdr@thmsintrue\cdr@thmsasfalse\def\@NumberTheorems{#1}}}}
  \NumberTheoremsIn{section}%
\def\NumberTheoremsAs#1{\@ifempty{#1}%
     {\cdr@thmsasfalse}%
     {\@ifundefined{c@#1}{\@nocounterr{#1}}%
       {\cdr@thmsinfalse\cdr@thmsastrue\cdr@thm@necountertrue\def\@NumberTheorems{#1}}}}
  \NumberTheoremsAs{}%
\def\SwapTheoremNumbers{\def\thm@swap{S}}
\def\NoSwapTheoremNumbers{\def\thm@swap{N}}
  \NoSwapTheoremNumbers
\def\cdr@thmdefs{%
  \theoremstyle{plain}
  \ifcdr@thm@necounter
  \ifcdr@thmsin
  \newcounter{cdrthm}[\@NumberTheorems]%
  \xdef\thecdrthm
         {\expandafter\noexpand\csname the\@NumberTheorems\endcsname
           \@thmcountersep\@thmcounter{cdrthm}}%
    \gdef\cdr@thm{cdrthm}%     
    \else
    \ifcdr@thmsas
    \xdef\cdr@thm{\@NumberTheorems}%
    \else
    \newcounter{cdrthm}%
    \gdef\cdr@thm{cdrthm}%     
    \fi\fi\fi
\ifcdr@thm@necounter
  \newtheorem{theo}[\cdr@thm]{\theoname}%
  \newtheorem{prop}[\cdr@thm]{\propname}%
  \newtheorem{conj}[\cdr@thm]{\conjname}%
  \newtheorem{ques}[\cdr@thm]{\quesname}%
  \newtheorem{coro}[\cdr@thm]{\coroname}%
  \newtheorem{lemm}[\cdr@thm]{\lemmname}%
  \theoremstyle{definition}%
  \newtheorem{defi}[\cdr@thm]{\definame}%
  \theoremstyle{remark}%
  \newtheorem{nota}[\cdr@thm]{\notaname}%
  \newtheorem{notas}[\cdr@thm]{\notasname}%
  \newtheorem{rema}[\cdr@thm]{\remaname}%
  \newtheorem{remas}[\cdr@thm]{\remasname}%
  \newtheorem{exam}[\cdr@thm]{\examname}%
  \newtheorem{exams}[\cdr@thm]{\examsname}%
\else
\ifcdr@thmsin
  \newtheorem{theo}{\theoname}[\@NumberTheorems]%
  \newtheorem{prop}{\propname}[\@NumberTheorems]%
  \newtheorem{conj}{\conjname}[\@NumberTheorems]%
  \newtheorem{ques}{\quesname}[\@NumberTheorems]%
  \newtheorem{coro}{\coroname}[\@NumberTheorems]%
  \newtheorem{lemm}{\lemmname}[\@NumberTheorems]%
  \theoremstyle{definition}%
  \newtheorem{defi}{\definame}[\@NumberTheorems]%
  \theoremstyle{remark}%
  \newtheorem{nota}{\notaname}[\@NumberTheorems]%
  \newtheorem{notas}{\notasname}[\@NumberTheorems]%
  \newtheorem{rema}{\remaname}[\@NumberTheorems]%
  \newtheorem{remas}{\remasname}[\@NumberTheorems]%
  \newtheorem{exam}{\examname}[\@NumberTheorems]%
  \newtheorem{exams}{\examsname}[\@NumberTheorems]%
\else
  \newtheorem{theo}{\theoname}%
  \newtheorem{prop}{\propname}%
  \newtheorem{conj}{\conjname}%
  \newtheorem{ques}{\quesname}%
  \newtheorem{coro}{\coroname}%
  \newtheorem{lemm}{\lemmname}%
  \theoremstyle{definition}%
  \newtheorem{defi}{\definame}%
  \theoremstyle{remark}%
  \newtheorem{nota}{\notaname}%
  \newtheorem{notas}{\notasname}%
  \newtheorem{rema}{\remaname}%
  \newtheorem{remas}{\remasname}%
  \newtheorem{exam}{\examname}%
  \newtheorem{exams}{\examsname}%
\fi\fi
  \theoremstyle{definition}%
  \newtheorem*{defi*}{\definame}%
  \theoremstyle{remark}%
  \newtheorem*{nota*}{\notaname}%
  \newtheorem*{notas*}{\notasname}%
  \newtheorem*{rema*}{\remaname}%
  \newtheorem*{remas*}{\remasname}%
  \newtheorem*{exam*}{\examname}%
  \newtheorem*{exams*}{\examsname}%
  \theoremstyle{plain}%
  \newtheorem*{theo*}{\theoname}%
  \newtheorem*{prop*}{\propname}%
  \newtheorem*{conj*}{\conjname}%
  \newtheorem*{ques*}{\quesname}%
  \newtheorem*{coro*}{\coroname}%
  \newtheorem*{lemm*}{\lemmname}%
}
\def\cdr@enoncedef{%
 \newenvironment{enonce}[2][plain]%
    {\let\cdrenonce\relax \theoremstyle{##1}%
      \ifcdr@thm@necounter
      \newtheorem{cdrenonce}[\cdr@thm]{##2}%
      \else
      \ifcdr@thmsin
      \newtheorem{cdrenonce}{##2}[\@NumberTheorems]%
      \else
      \newtheorem{cdrenonce}{##2}%
      \fi\fi
     \begin{cdrenonce}}%
    {\end{cdrenonce}}%
 \newenvironment{enonce*}[2][plain]%
    {\let\cdrenonce\relax \theoremstyle{##1}%
     \newtheorem*{cdrenonce}{##2}%
     \begin{cdrenonce}}%
    {\end{cdrenonce}}%
}
\AtBeginDocument{%
\cdr@thmdefs
\cdr@enoncedef}
\def\propname{Proposition}%
\def\conjname{Conjecture}%
\def\quesname{Question}%
\def\notaname{Notation}%
\def\notasname{Notations}%
\def\theoname{Theorem}%
\def\coroname{Corollary}%
\def\lemmname{Lemma}%
\def\definame{Definition}%
\def\remaname{Remark}%
\def\remasname{Remarks}%
\def\examname{Example}%
\def\examsname{Examples}%
\def\equalenv#1#2{%
\newenvironment{#1}{\begin{#2}}{\end{#2}}}
\equalenv{theorem}{theo}
\equalenv{thm}{theo}
\equalenv{thm*}{theo*}
\equalenv{lemma}{lemm}
\equalenv{conjecture}{conj}
\equalenv{question}{ques}
\equalenv{exem}{exam}
\equalenv{exems}{exams}
\equalenv{exem*}{exam*}
\equalenv{exems*}{exams*}



\def\enddoc@text{%
 \begingroup
 \def\nobreakauthor{\relax}%%
 \def\and{\relax}%%
   \def\firstname##1{\relax}%
    \def\lastname##1{\relax}%
    \def\middlename##1{\relax}%
    \def\vonname##1{\relax}%
    \def\junior##1{\relax}%
    \edef\@tmpa{\authors}
    \fontdimen2\font=0pt\fontdimen3\font=0pt\fontdimen4\font=0pt\relax
  \sbox\@tempboxa{\relax\@tmpa}%
  \ifdim\wd\@tempboxa>\z@%
  \ClassError{\@classname}{%
   No printable char should be placed outside of name commands for
   authors names (firstname, lastname, middlename, vonname,
   junior). If you want to insert a nonbreakable space, please use nobreakauthor!
      }{%
RTFM!
      }%
\fi
\endgroup
\ifx\@empty\@translators \else\@settranslators\fi
  \ifx\@empty\addresses \else\@setaddresses\fi}

\endinput
