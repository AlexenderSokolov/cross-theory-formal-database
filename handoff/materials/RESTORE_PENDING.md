# Restore the safe pending materials

This package holds all40 source-admitted IDs outside the fixed safe975 release, plus the separate safe IN_PROGRESS1907 partial handoff. Twenty-seven IDs already belong to LOCAL1002; thirteen have separately root-cleared canonical packets. The status list is [PENDING_STATUS.json](PENDING_STATUS.json), and [PENDING_INDEX.md](../pending/PENDING_INDEX.md) links the complete40 standalone TeX browse copies and1907's partial components.

The archive has1,653 repository-relative paths and1,508 unique SHA256 objects. Its whole SHA256 is3d5c35bb240f0e2ae751a7fde88b982c0166f91e1552bb8b8d2e57c0218f18d3 and its exact size is31,634,324 bytes. Eight ordered binary parts carry it; parts1–7 are4,194,304 bytes and part8 is the remainder. Every part has its own hash in pending-materials.transport.json. The current CAS manifest SHA256 is26ea39757fa5106c57c8ac0cdb703af589ff9832f0a8c29ec4c12d03d2cab567. It binds actual safe current bytes and restore paths relative to the handoff directory.

From the repository root, first enter handoff. Run all commands below with handoff as the working directory, with Python3 and these files present:

```sh
cd handoff
python3 materials/restore_pending.py \
  --expected-transport-sha256 1f2af3c11d6d9527a0bdd4de7145859deb7f280196e131fdbedb6af4e962b1a5 \
  --destination .
```

This verifies the transport manifest, every ordered part, the whole archive, the CAS manifest and every blob before restoration. It reassembles materials/pending-materials.cas.zip locally, then uses the unchanged tested fail-closed CAS restore kit. It accepts an identical existing file and mode and refuses to replace a differing file or traverse symlinks. All restored paths stay under the selected destination. Public Git copies use ordinary0644 modes; original canonical source artifact bytes and modes were preserved. Restore requires only these repository files and Python's standard library, with no cloud temporary directory or download. Restoration expands65,260,432 logical file bytes and reassembles the31,634,324-byte ZIP.

Verify the complete current package with its carried actual build artifacts:

```sh
python3 pending/runtime/scripts/validate_corpus.py \
  --mode editable-delivery --package pending/package \
  --evidence pending/package/delivery-evidence.json \
  --build-root pending/build --report pending40-local-validation.json
```

The actual initial per-item CLI qualified all40, and the actual aggregate qualified40. A full offline roundtrip restored every1,653 path to real files, verified all hashes/sizes/modes, and ran the unchanged aggregate CLI again:40 qualified, no errors. Restored constrained SQLite has40 problems and39 sources, integrity ok, no foreign-key failures and exact complete TeX in every full-text row. Five current canonical-only group SQLite snapshots are also carried. ACTUAL-ROUNDTRIP-RECEIPT.json and ROUNDTRIP-PORTABLE40-ACTUAL-CLI.json record those checks. The restore kit and ordered-part safety checks passed30 tests.

For fresh compilation, use the complete restored package item paths instead of the browse copies. The full package carries required graphics and exact filename aliases, complete original licensed PDFs, editable core/bibliography/source bindings, current provenance and notices, actual compiler/final logs and receipts. It requires installed XeLaTeX, pypdf, genuine standard TeX packages and the fonts named in the TeX: Latin Modern Roman, NotoSerif and NotoSansMath-Regular.ttf where used; CM, RSFS, Euler and the other recorded TeX font designs are system prerequisites. Installed dependency/font identity pins in each item's runtime metadata document the tested environment; those old absolute paths are historical recorder evidence, not restore inputs. No fonts, private publisher classes, nonexclusive native aids or upstream archives are redistributed.

The genuine IEEEtrantools1.5 dependency, acquisition attribution and LPPL1.3 license for1505 are in pending/package/sources/1505/runtime. Preserve its SHA25689b8d8efe9416b99d1d3497a18d948cfb8c3e87e03cb2412f3a9177d5c6ea7bf and use the package-local TEXINPUTS recipe:

```sh
export TEXINPUTS="$PWD/pending/package/sources/1505/runtime//:"
python3 pending/runtime/scripts/compile_editable_delivery.py \
  --package pending/package --build-root local-fresh-build \
  --receipt-root local-fresh-receipts
python3 pending/runtime/scripts/validate_corpus.py \
  --mode editable-delivery --package pending/package \
  --evidence pending/package/delivery-evidence.json \
  --build-root local-fresh-build --receipt-root local-fresh-receipts \
  --report pending40-fresh-local-validation.json
```

The40 standalone TeX bytes are unchanged from the current admitted bodies. Original warnings, page layouts, source quirks and conditional hypotheses remain.1560/1598/1599 use the root-cleared final revision;1598 is explicitly conditional,1599 retains the full preemption/speed/epsilon model and inactive604–609 newline-preserving exclusion.1907 remains unqualified, uncounted and incomplete: its seven approved files contain the original licensed PDF, safe factual grant witness, partial statement and Corollary2.15 components, exact status and continuation instructions. Its private full draft is excluded.

Current LOCAL1002 notices are used for1538/1545, with1538's source-level license locator pointing to1536 for the shared source.1905 uses the minimal factual safe CC4 witness SHA256942acf0ac5084707be87e41c6fe6d3a179cd4ca9913c5085baf781516e62a36f. Historical canonical group/PUBLISH hashes remain in pending/historical-group-identities.json as provenance; current-safe-metadata-differences.json records locator and safe-byte changes. Old source approval records and comparison hashes remain dated witnesses. The current CAS filemap is the complete portable file authority. Unnecessary derivative QA rasters, superseded historical copies, raw HTML/session fields, private native aids/archives/classes and source fonts are excluded. Every original licensed PDF and genuine required asset is retained.
