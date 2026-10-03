# Independent review of the exact published origin schema proposal

Approved narrowly for root review/integration: the publisher proposal only adds human_authored_checked_published_transcription to the existing problems.origin_class CHECK enum. Every other DDL byte is identical to the old frozen885/assembled schema. No relabeling, runtime relaxation, schema integration, publisher file edit or remote action was performed here.

Actual old-schema RED reproduces CHECK rejection for a valid minimal new-origin row. The exact publisher proposal then passes17 independent actual-SQLite tests with zero skips. These exercise old/new origins, difficulty/status checks, duplicate IDs and TeX paths, original NOT NULL constraints, foreign-key insert/update/delete guards, and unchanged table/index/column/FK topology.

Path checks at SQL level are the original UNIQUE and NOT NULL constraints. Filesystem scope is enforced separately by the unchanged delivery validator; this proposal adds no path-check DDL.

Run: PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v

Root must decide integration. All911 fresh explicit per-item CLI runs and a fresh aggregate remain required after the fix. See reports/REVIEW.json, reports/schema.diff and the preserved RED/GREEN logs.
