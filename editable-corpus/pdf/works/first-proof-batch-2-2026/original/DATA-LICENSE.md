# Data license & provenance

This file records, for each kind of material in this repository, who produced it
and on what basis First Proof publishes it. `NOTICE` states the licenses; this
file states the provenance behind them.

The governing principle: **First Proof licenses only what First Proof produced or
holds the rights to.** Nothing here is a blanket grant over third-party work.

## Covered by CC-BY-SA-4.0 (see `LICENSE-DOCS`)

**Problem statements.** Written and curated by First Proof for this batch.

**Human solutions** (`batch-2-human-solution/`). Written for First Proof as part
of the benchmark design, and published as part of it.

**AI-generated solutions** (`batch-2-AI-solutions/`) **and raw run outputs**
(`batch-2-raw-outputs/`). These are the outputs of runs First Proof commissioned,
configured and executed. Under the benchmarking protocol in `batch-2-design/`,
First Proof supplied the common input file, owned and operated the run
infrastructure, ran each submitter's container on the requested hardware, and
collected everything written to the output directory. The resulting corpus —
solutions, thinking traces, token logs, run metadata, and any scratch code the
models wrote while working — is published by First Proof as the evidence base the
benchmark exists to produce. The scratch code is a run artifact and is licensed
CC-BY-SA-4.0 with the rest of the output, not AGPL-3.0.

**Referee reports** (`batch-2-reviews/`). Published on the basis on which they
were solicited: referees were told that all data from the batch would be released
publicly, and they wrote their comments into review documents First Proof
generated and supplied for that purpose. The reports are published anonymized —
each is identified by a stable reviewer number within its submission, not by
name. A referee is named only with their written consent.

**Documentation.** READMEs, protocol specifications, annotation protocols and
editorial material authored by First Proof.

## Covered by AGPL-3.0 (see `LICENSE`)

Source code First Proof wrote: the benchmarking protocol, `run.sh`, the
configuration templates and the reference submission under `batch-2-design/`, and
the model-testing harness under `batch-2-modeltesting/`.

## NOT licensed here — third-party submitter code

    batch-2-submissions/improofbench/
    batch-2-submissions/princeton/
    batch-2-submissions/ucla/

These are the submitters' own codebases, contributed so that First Proof could run
them against the batch. They are **not** First Proof's work, are **not** covered by
either license file here, and remain the copyright of their authors under whatever
terms those authors set. None of the three carries a license file of its own, so no
permissions should be assumed from their presence in this repository; approach the
authors. `improofbench` is additionally derived from MathArena and carries that
project's upstream terms.

## Future material

Any later contribution that originates with another author or submitter is **not**
swept under the grants above. It is published only with permission, licensed
CC-BY-SA-4.0 where First Proof holds the rights, and otherwise marked
"© respective authors, published with permission." Where the rights status of any
material is unclear, it is flagged and withheld rather than published.

## Relationship to First Proof's DARPA agreement

The material in this repository was produced **before** DARPA agreement
HR0011263E126 took effect (21 July 2026) and was not generated under it. The
Government's Unlimited Rights under that agreement attach to data developed or
generated under the agreement, and therefore do not reach this batch. The licenses
above are First Proof's own grants to the public and are unaffected by it.
