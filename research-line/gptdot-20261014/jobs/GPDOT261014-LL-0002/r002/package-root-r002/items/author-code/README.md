
# A formalization of Chevalley groups

A Lean verification of certain presentations of Chevalley-like groups.

The main theorem we formalize was first proved by Ryan O'Donnell and Noah G. Singer
in a [recent paper](https://arxiv.org/pdf/2411.05916). The main theorem states that in
a particular Chevalley-like group (the graded, unipotent B3-large group), a certain
subset of Steinberg relations is sufficient to install the entire group.

## Installing Lean

The main part of this repository is a mathematical formalization written in the Lean 4 theorem prover.
To install Lean on your machine,
see the [quickstart](https://lean-lang.org/lean4/doc/quickstart.html) guide from the Lean manual,
or [the extended setup instructions](https://lean-lang.org/lean4/doc/setup.html).
For development,
we recommend using the Lean 4 [VS Code extension](https://github.com/leanprover/vscode-lean4).

## Building the Lean formalization

At the root of this project, run:
```bash
lake exe cache get   # Downloads pre-built .olean files for mathlib
lake build           # Builds this project's main theorems
```

## Navigation

See `Steinberg/PROJECT_README.lean`.

## License

This project is licensed under the Apache 2.0 license (see [LICENSE](LICENSE)).
The "Steinberg Group" refers to the authors/contributors listed below.

## Authors and contributors

* Eric Wang <ejwang2@andrew.cmu.edu>
* Arohee Bhoja <arohee@cmu.edu>
* Cayden Codel <ccodel@andrew.cmu.edu>
* Noah Singer <ngsinger@cs.cmu.edu>
