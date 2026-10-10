"""Build this one local revision from exact archived author-source lines.

The original corpus is read-only. Compilation and qualification remain pending.
Running this again recreates the pending package; it does not retain a later
root qualification decision. No file is deleted and no receipt is fabricated.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil


REVISION = Path(__file__).resolve().parent
REPO = REVISION.parents[2]
ORIGINAL = REPO / "editable-corpus"
PACKAGE = REVISION / "package-root"
PID = "211538"
ITEM = f"items/{PID}_author_proof.tex"
SOURCE = f"sources/{PID}/source0.tex"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build():
    for name in ("items", f"sources/{PID}", "licenses"):
        (PACKAGE / name).mkdir(parents=True, exist_ok=True)
    original_tex = (ORIGINAL / ITEM).read_bytes()
    original_source = (ORIGINAL / SOURCE).read_bytes()
    source_lines = original_source.splitlines(keepends=True)
    original_manifest = json.loads((ORIGINAL / "manifest.json").read_text(encoding="utf-8"))
    old = next(x for x in original_manifest["items"] if x["problem_id"] == PID)
    original_licence = (ORIGINAL / old["license_path"]).read_bytes()
    assert sha(original_tex) == old["tex_sha256"], "Original item bytes differ from the pinned manifest (check CRLF conversion)."
    assert sha(original_source) == old["primary"]["source_sha256"], "Original source bytes differ from the pinned manifest."
    assert sha(original_licence) == "c42666636ead1b2ca5489c907b13e6af1a18a9bac45d54629792696fce7f491b", "Original licence differs from pinned Git bytes."
    original_copy = REVISION / "original"
    original_copy.mkdir(exist_ok=True)
    (original_copy / f"{PID}_author_proof.tex").write_bytes(original_tex)
    dump(original_copy / "manifest-item.json", old)
    shutil.copy2(ORIGINAL / SOURCE, PACKAGE / SOURCE)
    shutil.copy2(ORIGINAL / old["license_path"], original_copy / "license-notice.txt")
    shutil.copy2(ORIGINAL / old["license_path"], PACKAGE / old["license_path"])

    chunks = []
    block_map = []
    bodies = []

    def editorial(text):
        chunks.append(text.encode("utf-8"))

    def source_block(name, start, end, role="context", evidence=True):
        raw = b"".join(source_lines[start - 1:end])
        first = sum(chunk.count(b"\n") for chunk in chunks) + 1
        chunks.append(raw)
        last = first + len(raw.splitlines()) - 1
        normalized = "\n".join(raw.decode("utf-8").splitlines())
        block_map.append({"name": name, "role": role, "source_path": SOURCE,
                          "source_lines": [start, end], "new_tex_lines": [first, last],
                          "exact_bytes_equal": True, "exact_text_equal": True,
                          "source_block_sha256": sha(raw), "new_block_sha256": sha(raw)})
        if evidence:
            bodies.append({"role": role, "tex_lines": [first, last], "tex_sha256": sha(normalized.encode("utf-8")),
                           "source_index": 0, "source_lines": [start, end], "method": "exact_tex"})

    # Reuse the published, previously compiled preamble and document opening.
    chunks.append(b"".join(original_tex.splitlines(keepends=True)[:33]))
    editorial(r"\noindent\emph{Source and licence.} Vignon Oussa, arXiv:2609.27970v1. The inherited source metadata records CC BY 4.0. The bundled licence notice records the origin of that metadata and the exact contents of this local revision." + "\n\n")
    editorial(r"\noindent\textit{Editorial scope.} Counted unit: the author's lemma \texttt{lem:winding}, with its complete original proof. This revision restores the author's continued-fraction and Denjoy--Koksma context (source0.tex lines 1028--1059) and the four cited bibliography entries. The statement (1067--1076) and proof (1078--1177) are unchanged. Every mathematical excerpt and bibliography entry below is copied exactly from the bundled source. The published item is preserved separately." + "\n\n")
    editorial(r"\section*{Author context: irrational returns and Denjoy--Koksma}" + "\n\n")
    source_block("continued_fraction_and_Denjoy_Koksma", 1028, 1059)
    editorial("\n" + r"\section{The counted unit and the author's complete proof}" + "\n\n")
    source_block("primary_statement", 1067, 1076, "primary_statement")
    editorial("\n")
    source_block("primary_proof", 1078, 1177, "primary_proof")
    editorial("\n")
    source_block("bibliography_open", 2226, 2226, evidence=False)
    editorial("\n")
    for key, start, end in (("KatokHasselblatt", 2352, 2356), ("Khinchin", 2358, 2361),
                            ("KuipersNiederreiter", 2376, 2379), ("Petersen", 2462, 2466)):
        source_block("bibliography_" + key, start, end)
        editorial("\n")
    source_block("bibliography_close", 2468, 2468, evidence=False)
    editorial("\n" + r"\end{document}" + "\n")
    revised = b"".join(chunks)
    (PACKAGE / ITEM).write_bytes(revised)
    new_lines = revised.splitlines(keepends=True)
    for block in block_map:
        a, b = block["source_lines"]
        c, d = block["new_tex_lines"]
        assert b"".join(source_lines[a - 1:b]) == b"".join(new_lines[c - 1:d]), block["name"]
    for start, end in ((1067, 1076), (1078, 1177)):
        assert b"".join(source_lines[start - 1:end]) in original_tex
    assert revised.split(b"\\begin{document}", 1)[0] == original_tex.split(b"\\begin{document}", 1)[0]

    text = revised.decode("utf-8")
    labels = re.findall(r"\\label\{([^}]+)\}", text)
    references = re.findall(r"\\(?:eqref|ref)\{([^}]+)\}", text)
    citations = {key.strip() for group in re.findall(r"\\cite\{([^}]+)\}", text) for key in group.split(",")}
    bibliography = set(re.findall(r"\\bibitem\{([^}]+)\}", text))
    assert not (set(references) - set(labels))
    assert len(labels) == len(set(labels))
    assert citations == bibliography
    old_commands = set(re.findall(r"\\([A-Za-z]+)", original_tex.decode("utf-8")))
    new_commands = sorted(set(re.findall(r"\\([A-Za-z]+)", text)) - old_commands)
    assert set(new_commands) <= {"bibitem", "cite", "pmod", "quad", "texttt"}, new_commands

    reason = ("在无理旋转遍历性、沿连分数渐近分母的Denjoy–Koksma界、L2平移连续性作为明确先修时，"
              "本证明通过单位相位归一化和q_n次迭代取得相位积分趋1，再由非零绕数导致的相位导数下界及分部积分取得O(q_n^{-1})，形成矛盾。"
              "这是有实质内容的博士专题分析证明，建议H2；原H3理由仅依据研究论文与100行证明长度，不足以支持H3。")
    row = copy.deepcopy(old)
    row.update(difficulty_level="H2", difficulty_reason=reason, status="revision_pending_compile",
               tex_sha256=sha(revised), compile_receipt=f"receipts/{PID}.json",
               revision_of={"public_commit": "5c133eb3cb70ada8bd3ca187089fe69378e5bc52", "original_tex_sha256": sha(original_tex),
                            "original_difficulty_level": old["difficulty_level"], "revision_id": "211538-r001"})
    row["contexts"] = [{"source_file": SOURCE, "source_sha256": sha(original_source),
                        "start_line": b["source_lines"][0], "end_line": b["source_lines"][1], "scope": "context"}
                       for b in block_map if b["role"] == "context" and b["name"] not in ("bibliography_open", "bibliography_close")]
    check = {"complete_statement": True, "complete_proof": True, "required_context_preserved": True,
             "above_ordinary_phd_quals": True, "checked_at": "2026-10-10", "source_authorship": "named-human-author",
             "method": "independent full-primary reading plus exact author-source block comparison",
             "reviewer": "audit_current_state", "independent": True,
             "note": "Restored convergent denominators and Denjoy–Koksma statement/citations; primary text unchanged; H2 recommended. No fresh compile or visual verification claimed."}
    row["source_check"] = check
    manifest = {"schema_version": 1, "scope": "local revision candidate; pending fresh compilation and root qualification",
                "verified_count": 0, "package_item_count": 1, "items": [row]}
    dump(PACKAGE / "manifest.json", manifest)
    dump(PACKAGE / f"sources/{PID}/provenance.json", row)
    evidence = {"schema_version": 1, "package_manifest_sha256": sha((PACKAGE / "manifest.json").read_bytes()),
                "derivation_scope": "exact text and source-context verification only; no compile receipt yet",
                "items": {PID: {"item_sha256": sha(revised), "independent_problem_unit": True,
                                "claim_key": row["claim_key"], "source_check": check,
                                "sources": [{"root": "package", "path": SOURCE, "sha256": sha(original_source)}],
                                "bodies": bodies}}}
    dump(PACKAGE / "delivery-evidence.json", evidence)
    (PACKAGE / "INDEX.md").write_text("# 独立修订题包（编译待验证）\n\n| 题号 | 题名 | 难度 | 可编辑 TeX | 来源及定位 |\n|---|---|---|---|---|\n"
        + f"| {PID} | {row['title']} | H2 | [{PID}_author_proof.tex]({ITEM}) | [作者原文]({row['source_url']}) · [原文定位](sources/{PID}/provenance.json) |\n", encoding="utf-8")
    notice = ("Vignon Oussa\nThe critical mixed-arithmetic four-point HRT theorem\narXiv:2609.27970v1\n\n"
              "Recorded licence: Creative Commons Attribution 4.0 International, http://creativecommons.org/licenses/by/4.0/. "
              "This record is inherited from the original corpus manifest and licence notice for https://arxiv.org/abs/2609.27970v1; "
              "this revision does not claim a new publisher-metadata check. The original abstract-page capture is not present in this copied package.\n\n"
              "This local package contains the revised AMS wrapper, the unchanged bundled source0.tex, provenance, manifest, INDEX, exact-body evidence and the copied database preparation scripts. "
              "All retained mathematical text and the four bibliography entries are exact author-source excerpts. "
              "The revision changes editorial metadata and restores omitted author context; it does not change the statement or proof. "
              "No image assets, publisher class/style files, fonts or original compilation receipts are redistributed in this revision.\n")
    (PACKAGE / "licenses/REVISION-NOTE.txt").write_text(notice, encoding="utf-8")
    for name in ("schema.sql", "rebuild_database.py", "restore_database.py", "test_database.py", "test_restore_database.py"):
        shutil.copy2(ORIGINAL / name, PACKAGE / name)
    changes = {"problem_id": PID, "revision_id": "211538-r001", "reviewer": "audit_current_state",
               "original_file": "editable-corpus/" + ITEM,
               "preserved_original_copy": "original/211538_author_proof.tex", "new_file": "package-root/" + ITEM,
               "original_file_sha256": sha(original_tex), "new_file_sha256": sha(revised),
               "source_file": "package-root/" + SOURCE, "source_file_sha256": sha(original_source),
               "source_copy_bytes_equal": (PACKAGE / SOURCE).read_bytes() == original_source,
               "pinned_original_git_bytes_checked": True,
               "original_licence_sha256": sha(original_licence),
               "licence_copy_bytes_equal": (PACKAGE / row["license_path"]).read_bytes() == original_licence,
               "preamble_bytes_unchanged": True, "primary_statement_bytes_unchanged": True,
               "primary_proof_bytes_unchanged": True, "blocks": block_map,
               "editorial_changes": ["Replaced the isolated return equation context with author-source lines 1028–1059.",
                                      "Restored four author bibliography entries; preserved the original licence bytes and added a separate inventory note without new external licence claims.",
                                      "Changed only local revision metadata from inherited H3 to reviewed H2 recommendation; original main data unchanged."],
               "difficulty_review": {"original_level": "H3", "recommended_level": "H2", "rationale": reason,
                                     "previous_second_review": "curation/second-reviews.jsonl", "context_gap_repaired": True},
               "static_reference_check": {"missing_labels": [], "duplicate_labels": [], "missing_bibliography_keys": [],
                                          "cited_keys": sorted(citations), "new_control_words": new_commands,
                                          "new_controls_are_standard_latex": True},
               "compile_status": "not_run", "fresh_visual_status": "not_run", "root_qualification_status": "pending",
               "receipt_policy": "No original or fabricated compile receipt copied; root must compile the new bytes."}
    dump(REVISION / "changes.json", changes)
    print(json.dumps({"package": str(PACKAGE), "blocks_verified_exact": len(block_map),
                      "primary_unchanged": True, "missing_refs": [], "citations": sorted(citations),
                      "compile_status": "not_run"}, ensure_ascii=False))


if __name__ == "__main__":
    build()
