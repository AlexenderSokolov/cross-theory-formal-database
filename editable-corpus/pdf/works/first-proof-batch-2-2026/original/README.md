# First Proof — Second Batch

The second batch of the First Proof benchmark: ten research-level mathematics
problems, the human solutions, the submissions run against them, everything the AI
systems produced, and the anonymized referee reports on those attempts. Batch 2 was
graded at a workshop at Harvard CMSA on 4–5 June 2026.

## Contents

- `batch-2-design/` — the benchmarking protocol, First Proof's run script, and a
  reference submission
- `batch-2-submissions/` — the three submitters' codebases (**third-party — see
  Licensing**)
- `batch-2-modeltesting/` — First Proof's own model-testing harness
- `batch-2-raw-outputs/` — complete run outputs: solutions, thinking traces, token
  logs, run metadata
- `batch-2-AI-solutions/` — the AI-generated solutions, de-anonymized by submitter
- `batch-2-human-solution/` — the human solutions to the ten problems
- `batch-2-reviews/` — anonymized referee reports on the AI attempts

## Licensing

**First Proof licenses only what First Proof produced or holds the rights to.**

- Code First Proof wrote (`batch-2-design/`, `batch-2-modeltesting/`) —
  **AGPL-3.0** (`LICENSE`)
- Everything else First Proof produced or generated — problems, human solutions,
  AI solutions, raw run outputs, referee reports, documentation — **CC-BY-SA-4.0**
  (`LICENSE-DOCS`)
- The three submitters' codebases under `batch-2-submissions/` — **not licensed
  here.** They remain their authors' copyright; First Proof grants no rights in
  them. The outputs they produced when First Proof ran them *are* covered by the
  CC-BY-SA-4.0 grant.

`NOTICE` states the grants; `DATA-LICENSE.md` records the provenance behind each,
including the basis on which the referee reports are published.

## Links

- **Website:** <https://1stproof.org>
- **First batch:** <https://github.com/1stproof/batch-1> (paper:
  [arXiv:2602.05192](https://arxiv.org/abs/2602.05192))
- **Contact:** contact@1stproof.org
