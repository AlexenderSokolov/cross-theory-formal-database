# Exact LOCAL1002 reconstruction

Repository layout: the base is **repo/editable-corpus**; this kit is **repo/handoff/local1002**; shared pending objects are **repo/handoff/materials**. `handoff` is a directory within the repository, not the repository root. No cloud `/tmp` file is a restore dependency. Old paths inside original reviewed provenance remain historical strings and are never dereferenced by the restore kit.

This fixed projection is safe975 plus exactly27 selected additions, yielding1,002 primary units. The original3,000+ candidate catalog and the other13 pending material records are separate. The safe975 planned tree is669d8b47233a11ae40e8a7f4508f5b67df5274fb; the verified safe975 commit is5bb58ff2b57284a3ab2f2a76e50f588f4a8e629f; see [current handoff status](../STATUS_SNAPSHOT.json). Original dated evidence retains its pre-publication null/conditional fields. The safe975 branch/commit/tree has now been verified; restore still checks its exact bytes. This local kit performs no Git action.

The plan maps18,855 files:17,995 exact base-path/hash files,851 selected SHA blobs reused from the sealed pending40 CAS, and9 changed globals/full-textSQLite objects in six local overlay parts. It omits312 noninput derivative comparison rasters, superseded duplicate globals/boundary maps and stale1538/1545 historical notices, consistently with pending40. All source PDFs/carriers/full TeX, current notices, required assets, fidelity/input metadata and receipts are retained. This bounded projection received an actual1002 aggregate and completeSQL/source/fulltext acceptance.

## Offline reconstruction

Run from any working directory, using an absolute repository path:

```bash
python3 /path/to/repo/handoff/local1002/restore_local1002.py \
  --repo /path/to/repo --output /path/to/repo/local-state/local1002
```

The output must be new. Exact unchanged base files are hardlinked, so choose an output on the same filesystem as repo/editable-corpus; no automatic full-base copy is performed. The9 overlay globals/SQLite and851 pending inputs are normally decoded from hash-verified CAS objects and written. Keep inputs immutable and compile only into new external build/receipt directories. Default reconstruction needs roughly125MiB of new file allocation plus directory overhead; provide extra free space. A read-only verified existing1002 cache may be supplied with `--verified-cache` to reuse exact data by hardlink.

For whole-plan/CAS/base identity verification without materializing output:

```bash
python3 /path/to/repo/handoff/local1002/restore_local1002.py \
  --repo /path/to/repo --output /path/to/repo/local-state/unused-new-path --verify-only
python3 -B -m unittest discover -s /path/to/repo/handoff/local1002 -v
```

The script rejects changed base bytes/modes, missing or altered parts/objects, path traversal, symlinks, duplicate JSON/path/archive entries and an existing output. It never downloads, executes blob code, changes production gates, writes Git or deletes originals. The exact reconstructed SQLite is included, so no cloud database, old975 chunks or nondeterministic rebuild is needed.

## Acceptance and remaining gates

The actual acceptance directory contained every18,855 planned file using read-only hardlinks for base/shared/global inputs. Both CAS archives and every selected overlay object, including the67,211,264-byteSQLite, were independently streamed/decompressed and verified against exact hashes. Because of the disk limit, this was **full hardlink materialization plus complete archive stream verification**, not a claim that all files were written afresh from archives. Separate positive/negative fixtures exercise real archive writes. The production restore supports such writes when local space is available.

On that actual directory, the clean-environment unchanged validator returned1,002/1,002 with no errors; SQLite integrity/FK and everyfull TeX/source/locator projection passed. Existing975 checks were retained only after exact material/build/runtime/INDEX/SQL reconciliation against safe975r004, using its latest safe5 reports. The27 new units have54 actual successful per-item invocations across two current-context rounds, with27 unique additions; there were zero fresh975 per-item calls in this task.

`milestone_policy.py` is the separately tested explicit real975→1002 policy adapter. The original ledger helper/production validator/schema remain unchanged. The10 policy tests refuse changed material/runtime/projections, missing prior/base bindings/fresh27/fullaggregate and superseded unsanitized bases. Do not use this fixed-count adapter to fake later milestones.

The included compressed evidence decodes to exact current reports. `LOCAL1002-ACCEPTANCE.json` describes their pins and the hardlink/stream distinction. The original larger scratch1002 inventory is historical prepared evidence; the reconstruction plan defines this smaller tested public projection.

For a fresh local build after restoring, install the recorded Python3.12/pypdf6.10/XeLaTeX/TeXLive/fonts dependencies from official sources, then use the unchanged repo/corpus-work/scripts/compile_editable_delivery.py with external build/receipt roots and `--engine xelatex`. Include the declared genuine1505 runtime directory in TEXINPUTS. Run repo/corpus-work/scripts/validate_corpus.py --mode editable-delivery with the restored package/evidence, fresh build root and `--receipt-root` override. See LOCAL-30000-EXPANSION-HANDOFF.md for full commands and source/difficulty/rights/dedup rules.

Before claiming a published1002 release or30,000 completed problems, the sole publisher still needs actual safe975 commit/tree/ref readback, final1002 publication/restore/object/tree verification and honest separate remote counters. No new intake beyond this fixed1002 is included.
