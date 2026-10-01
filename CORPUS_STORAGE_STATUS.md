# Corpus tooling snapshot

This branch contains the current fail-closed collection, compilation and validation tooling and its tests. Existing repository reference materials are preserved.

The full source corpus is still being collected toward3000 qualified unique human-proof problems. This initial code-only snapshot is NOT a complete corpus backup and cannot validate the corpus until its original source files, metadata, manifests and compile receipts are restored. No completion claim is made here.

The normal file-backed corpus remains authoritative. SQLite is proposed as a rebuildable search index, not yet implemented. Large original PDFs and complete recovery archives are not ordinary Git objects in this snapshot. Component source licenses must be preserved; no blanket license is applied.

See corpus-work/README_CURRENT.md and EXECUTION_PLAN.md for the actual pipeline. Run tests from corpus-work with python3 -m unittest discover -s tests -v.
