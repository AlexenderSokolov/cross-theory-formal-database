# Auxiliary assessments — 2026-10-14

These Markdown reports assess material records at fixed snapshot `41b4ab870b5b24d235c74e7123bccba6d9b9b042`. They are independent maintenance assessments, not formal human content reviews, and do not change production records, review/deduplication states, H2/H3 qualifications, or qualification counts. The [fixed manifest](https://github.com/AlexenderSokolov/cross-theory-formal-database/blob/41b4ab870b5b24d235c74e7123bccba6d9b9b042/editable-corpus/manifest.json) is the population reference: **19,789 material rows = 14,875 legacy + 4,914 prepared**.

| Read | Purpose |
| --- | --- |
| [Difficulty assessment overview](difficulty_assessment_overview.md) | Scope, evidence boundaries, and the three eight-item assessments. |
| [Historical eight-item assessment](historical8_assessment.md) | Bounded assessment of the historical sample. |
| [Prepared eight-item assessment](prepared8_assessment.md) | Bounded assessment of the prepared sample. |
| [Reviewed eight-item assessment](reviewed8_assessment.md) | Bounded assessment of the reviewed sample. |
| [Source diversity and overlap](source_diversity_overlap.md) | All/legacy/prepared counts, normalization limits, attribution conflict, and eleven overlap cases. |
| [Read-only source metadata helper](source_metadata_statistics.py) | Recompute metadata statistics from the fixed manifest. |
| [Helper unit tests](test_source_metadata_statistics.py) | Small normalization, coverage, and concentration checks. |

Run from the repository root with Python 3:

```sh
python3 docs/assessments/2026-10-14/source_metadata_statistics.py --repo . --snapshot 41b4ab870b5b24d235c74e7123bccba6d9b9b042
python3 -m unittest discover -s docs/assessments/2026-10-14 -p test_source_metadata_statistics.py -v
```

Read the evidence limits before interpreting metadata counts as independently distinct works, people, publication years, claims, or duplicates. Reproduction commands are not a claim that final validation has passed; that evidence belongs with the maintenance review.
