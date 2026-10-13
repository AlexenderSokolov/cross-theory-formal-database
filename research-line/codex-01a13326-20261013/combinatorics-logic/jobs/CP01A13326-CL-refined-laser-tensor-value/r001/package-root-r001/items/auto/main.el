(TeX-add-style-hook
 "main"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "11pt")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("algorithm2e" "linesnumbered" "boxed" "ruled" "vlined") ("ulem" "normalem") ("inputenc" "utf8")))
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "article"
    "art11"
    "amsfonts"
    "amsmath"
    "amsthm"
    "amssymb"
    "fullpage"
    "comment"
    "enumerate"
    "soul"
    "color"
    "mathrsfs"
    "mathdots"
    "algorithm2e"
    "bbm"
    "url"
    "tabu"
    "xfrac"
    "ulem"
    "inputenc")
   (TeX-add-symbols
    '("PK" 2)
    '("MOD" 1)
    "RP"
    "SYM"
    "MAJ"
    "classP"
    "classnP"
    "THR"
    "ETHR"
    "AnD"
    "OR"
    "DOR"
    "LEQ"
    "SETH"
    "SAT"
    "OV"
    "DISJ"
    "argmax"
    "argmin"
    "poly"
    "polylog"
    "sr"
    "xr"
    "yr"
    "zr"
    "rr"
    "trr"
    "tsr"
    "qr"
    "tqr"
    "F"
    "R"
    "n"
    "Q"
    "E"
    "Var"
    "Rest"
    "eps"
    "T"
    "X"
    "Y"
    "Z")
   (LaTeX-add-labels
    "sec:prelims"
    "thm:schonhage"
    "thm:SS"
    "sec:newidea"
    "thm:newidea"
    "thm:opt1"
    "thm:opt2"
    "sec:proof"
    "thm:main"
    "eq:valboundn"
    "subsec:step3"
    "sec:heuristics"
    "subsec:optgamma"
    "prob2"
    "subsec:heuristics"
    "heur:2"
    "sec:final-answer"
    "subsec:Tpart"
    "app:rounding"
    "app:powermean"
    "lem:apppowermean"
    "eqtoprove"
    "eqpowermean")
   (LaTeX-add-environments
    '("proofof" 1)
    '("reminder" 1))
   (LaTeX-add-bibliographies
    "papers")
   (LaTeX-add-amsthm-newtheorems
    "theorem"
    "lemma"
    "proposition"
    "corollary"
    "observation"
    "property"
    "example"
    "counterexample"
    "openproblem"
    "assumption"
    "conjecture"
    "fact"
    "remark"
    "definition"
    "problem"
    "question"))
 :latex)

