# Corpus storage and recovery entry points

This repository contains editable proof materials, source and license evidence, delivery metadata, and collection/validation tooling. Existing reference materials and recovery history are preserved.

The production goal is 30,000 qualified unique human-proof problems; see [PROJECT.md](PROJECT.md) and the [local controller handoff](LOCAL_CONTROLLER_HANDOFF.md). Material totals, historical labels and prepared records are not current-standard qualification counts. The [root README](README.md) records the reviewed delivery scope and its limits.

SQLite full-text projection and recovery are implemented, but a standalone `corpus.sqlite` is not tracked. See the [corpus guide](editable-corpus/README.md) for the distinction between the historical [delivery recovery description](editable-corpus/RECOVERY_CURRENT.md) and the revision-v2 [prepared database descriptor](editable-corpus/prepared-database.json). Use the manifest, descriptor and helper from the same recovery scope; legacy `schema.sql`/`rebuild_database.py` are not a general rebuild path for revision-v2 materials. Component source licenses must be preserved; no blanket license is applied.

The [project skill](corpus-work/.agents/skills/human-proof-corpus/SKILL.md) defines the production contract. [README_CURRENT.md](corpus-work/README_CURRENT.md) and [EXECUTION_PLAN.md](corpus-work/EXECUTION_PLAN.md) retain historical snapshots/plans. Reuse unchanged successful validation evidence; rerun only checks affected by an actual input or program change.
