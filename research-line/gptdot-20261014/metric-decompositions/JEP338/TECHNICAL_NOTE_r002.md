# r002: native arrow macro restoration

The parent reported an actual r001 compile failure: undefined `\mto`, generated line431. The preparation wrapper accidentally began its native macro extraction at original line40, omitting line39.

The exact definition in the untouched official publisher TeX, line39, is:

```tex
\newcommand\mto{\mathchoice{\longmapsto}{\mapsto}{\mapsto}{\mapsto}}
```

r002 copies this definition verbatim into presentation/preamble-r002.tex. This preserves the author's long mapping arrow in display style and ordinary mapping arrow in other styles. It is not a mathematical change or a guessed mapping.

All original newcommand/renewcommand/DeclareMathOperator definitions used in the selected body were compared by command names against the wrapper; mto was the only missing native definition. All six original let aliases (ts, oldbullet, wtd, ov, Ga, ga) are present. Other selected commands are supplied by the standard LaTeX/AMS, mathtools, tikz-cd, xfrac and hyperref packages already declared. No cedram-only selected-body command was found. This is a source/wrapper inspection, not a compile result.

The unchanged original source and r001 preamble remain in place. The original r001 task and report are preserved in revisions/r001. Canonical task.json now selects r002 and its explicit public whitelist selects only the new effective preamble and this technical note, excluding r001 archives and private files. No jobs, assembly, compile, QA, database or author mathematics were changed by the material worker.
