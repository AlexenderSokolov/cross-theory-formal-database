\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{sthesis}[2014/08/16 Steven's thesis latex class]

% \LoadClass{smath}


\LoadClass[11pt,a4paper]{report}
\RequirePackage[utf8]{inputenc}
\RequirePackage{amsmath}
\RequirePackage{amsthm}
\RequirePackage{amssymb}
\RequirePackage{graphicx}
\RequirePackage{float}
\RequirePackage{bm}
\RequirePackage{ifthen}
\RequirePackage{titlesec}
\RequirePackage{scrextend}
\RequirePackage{imakeidx}
\RequirePackage[hidelinks, hyperindex]{hyperref}
\RequirePackage{enumerate}
\RequirePackage{caption}
\RequirePackage[capitalise]{cleveref}
\RequirePackage{mathtools}
\RequirePackage{etoolbox}
\RequirePackage{bookmark}
\RequirePackage{subfiles}
\RequirePackage{xfrac}
\RequirePackage{subcaption}
\RequirePackage{adjustbox}
\RequirePackage{mwe}
\RequirePackage{soul}
\RequirePackage{stmaryrd}
\RequirePackage{setspace}

% Create usefull abreviations
\renewcommand{\a}{\alpha}
\renewcommand{\b}{\beta}
\newcommand{\g}{\gamma}
\newcommand{\C}{\mathcal{C}}
\newcommand{\R}{\mathbb{R}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\T}{\mathcal{T}}
\renewcommand{\S}{\mathcal{S}}
\newcommand{\of}{\subseteq}
\newcommand{\imp}{\rightarrow}
\newcommand{\E}{\exists}
\newcommand{\A}{\forall}
\newcommand{\arrow}{\longrightarrow}
\newcommand{\abs}[1]{\lvert #1 \rvert}
\renewcommand{\mod}[0]{\;\text{mod}\;}
\let\empty\varnothing
\newcommand{\ol}[1]{\overline{#1}}
\def\disobeylines{\catcode`\^^M=5 }
\def\multiset#1#2{\ensuremath{\left(\kern-.3em\left(\genfrac{}{}{0pt}{}{#1}{#2}\right)\kern-.3em\right)}}
\DeclarePairedDelimiter\ceil{\lceil}{\rceil}
\DeclarePairedDelimiter\floor{\lfloor}{\rfloor}
\let\formalphi\phi
\let\phi\varphi


\renewcommand{\:}[0]{\texttt{:}}
\renewcommand{\.}[0]{.\;}
\newcommand{\1}[0]{\textbf{1}}
\newcommand{\TODO}[0]{\textbf{TODO}}

\newcommand{\tup}[1]{\langle#1\rangle}

\newcommand{\pr}[1]{\texttt{pr#1}}
\newcommand{\idc}[1]{\text{id}_{#1}}
\newcommand{\inlc}[0]{\text{inl}}
\newcommand{\inrc}[0]{\text{inr}}
\newcommand{\inl}[0]{\texttt{inl}}
\newcommand{\inr}[0]{\texttt{inr}}
\newcommand{\zero}[0]{\textbf{0}}
\newcommand{\one}[0]{\textbf{1}}
\newcommand{\RecZ}[0]{\texttt{rec}_\textbf{0}}
\newcommand{\RecPlus}[0]{\texttt{rec}_+}
\newcommand{\id}[1]{\texttt{id}_{#1}}
\newcommand{\refl}[0]{\texttt{refl}}
\newcommand{\U}[0]{\mathcal{U}}
\renewcommand{\L}[0]{\mathcal{L}}

\newcommand{\betar}[0]{\overset{\beta}{=}}
% \newcommand{\judg}[0]{\overset{j}{=}}

\newcommand{\define}[3]{\newcommand{#1}[0]{\hyperref[def:#2]{#3}}\label{def:#2}\index{\hyperref[def:#2]{$#3$}}}

% Define theorems and definitions

\theoremstyle{definition}
\newcounter{theorems}
\counterwithin{theorems}{section}
\counterwithin{equation}{chapter}


\newtheorem{theorem}[theorems]{Theorem}
\newtheorem{corollary}[theorems]{Corollary}
\newtheorem{lemma}[theorems]{Lemma}
\newtheorem{definition}[theorems]{Definition}
\newtheorem{note}[theorems]{Note}
\newtheorem{proposition}[theorems]{Proposition}
\newtheorem{example}[theorems]{Example}
\newtheorem{notation}[theorems]{Notation}
\newtheorem{axiom}[theorems]{Axiom}

\crefname{figure}{Figure}{Figures}
\crefname{enumi}{item}{items}
\crefname{equation}{Equation}{Equations}
\creflabelformat{theorems}{#2#1#3}

\setlength\parindent{0pt}

\expandafter\def\expandafter\normalsize\expandafter{%
    \normalsize%
    \setlength\abovedisplayskip{-6pt}%
    \setlength\belowdisplayskip{6pt}%
    \setlength\abovedisplayshortskip{-8pt}%
    \setlength\belowdisplayshortskip{2pt}%
}


\makeatletter
\let\c@equation\c@figure
\makeatother

\usepackage[margin=2.5cm]{geometry}
\usepackage{todonotes}
\usepackage{afterpage}
\usepackage{listings}
\usepackage{wrapfig}
\usepackage{proof}

\usepackage{aligned-overset}
\usepackage[format=plain]{caption}

% TIKZ
\usepackage{tikz}
\usetikzlibrary{automata, positioning, arrows, shapes, decorations.pathmorphing,calc}
\tikzstyle{curvy}=[dashed,decorate,yshift=0.3cm,decoration={snake,amplitude=3mm,segment length=8mm,post length=1mm}]
\tikzstyle{block}=[draw, rectangle]
\tikzset{
    ->,
    >=stealth,
    node distance=3cm,
    every state/.style={line width=0.8pt},
    initial text=$ $,
    minimum size=2em,
    inner sep=1
}
\RequirePackage{tikz-cd}

\DeclareUnicodeCharacter{0088}{ }
\newcommand\blankpage{%
    \null
    \thispagestyle{empty}%
    \addtocounter{page}{-1}%
    \newpage}