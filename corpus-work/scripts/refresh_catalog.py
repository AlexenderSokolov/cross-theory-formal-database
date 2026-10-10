"""Refresh the reader-facing catalog from the published manifest and scoped reviews.

Published bodies, manifests, receipts and SQLite parts remain reproducible. The
catalog exposes current corrections and review state without rewriting history.
"""
import argparse
import collections
import csv
import io
import json
from pathlib import Path
import re


STATUS_ZH = {"confirmed": "本轮内容已核准", "hold": "待返修，暂不采用",
             "needs_review": "难度或内容待复核", "not_reassessed": "沿用历史材料，未在本轮复核"}
THM_ENV = re.compile(r"\\begin\{((?:theorem|thm|lemma|lem|proposition|prop|corollary|cor|claim|fact)(?:\*|[A-Za-z]*))\}", re.I)


def reason_flags(reason):
    flags = []
    if "case analysis, intermediate estimates, comparison or induction arguments as the source words them" in reason:
        flags.append("generic_proof_operations")
    if "it is a research contribution of the article in" in reason and "and is therefore strictly above ordinary PhD qualifying level" in reason:
        flags.append("venue_as_difficulty")
    if reason.startswith("Selected the article's "):
        flags.append("material_description_as_difficulty")
    if "H3: a complete original research-paper" in reason and "the level reflects that length" in reason:
        flags.append("length_as_difficulty")
    return flags


def make_catalog(items, reviews):
    ids = [str(x["problem_id"]) for x in items]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate manifest problem_id")
    grouped = {}
    for review in reviews:
        pid = str(review["problem_id"])
        scope = review.get("review_scope", "content")
        if pid not in ids:
            raise ValueError("unknown reviewed problem_id: " + pid)
        if scope not in {"content", "title"}:
            raise ValueError("unknown review_scope: " + scope)
        key = (pid, scope)
        if key in grouped:
            raise ValueError("duplicate active review: " + str(key))
        if review.get("status") not in {"confirmed", "hold", "needs_review"}:
            raise ValueError("unsupported review status: " + str(review.get("status")))
        grouped[key] = review
    result = []
    for item in sorted(items, key=lambda x: str(x["problem_id"])):
        pid = str(item["problem_id"])
        flags = reason_flags(item.get("difficulty_reason", ""))
        title_review = grouped.get((pid, "title"), {})
        content_review = grouped.get((pid, "content"), {})
        state = "needs_review" if flags else "not_reassessed"
        confirmed_h = None
        reason = item.get("difficulty_reason", "")
        if content_review:
            state = content_review["status"]
            if state == "confirmed":
                level = content_review.get("difficulty_level")
                if level not in {"H1", "H2", "H3"} or not content_review.get("evidence") or not content_review.get("difficulty_reason"):
                    raise ValueError("confirmed content requires grade, evidence and reason: " + pid)
                second = content_review.get("second_review")
                second_agrees = (isinstance(second, dict)
                                 and second.get("status") == "confirmed"
                                 and second.get("difficulty_level") == "H3"
                                 and second.get("independent") is True
                                 and bool(second.get("reviewer"))
                                 and bool(second.get("evidence"))
                                 and content_review.get("independent_second_review_completed") is not False)
                if level == "H3" and (content_review.get("review_stage") == "needs_second_review" or not second_agrees):
                    state = "needs_review"
                else:
                    confirmed_h = level
            reason = content_review.get("difficulty_reason") or reason
        title = item["title"]
        if title_review and title_review["status"] == "confirmed":
            if not title_review.get("title") or not title_review.get("evidence"):
                raise ValueError("title correction requires title and evidence: " + pid)
            title = title_review["title"]
        match = re.search(r"(?:arxiv:|arxiv.org/(?:abs|pdf)/)(\d{4}\.\d{4,5}|[a-z.-]+/\d{7})(v\d+)?", item.get("source_id", "") + " " + item.get("source_url", ""), re.I)
        replacement = content_review.get("replacement") or {}
        result.append(dict(
            problem_id=pid, arxiv_id=match.group(1) if match else "",
            version=match.group(2) or "" if match else item.get("source_version", ""),
            title=title, published_title=item["title"], author=item.get("author", ""),
            claim=item.get("claim_key") or item.get("primary", {}).get("theorem", ""),
            H=item["difficulty_level"], published_H=item["difficulty_level"], confirmed_H=confirmed_h,
            qualification_status=state, difficulty_reason=reason,
            published_difficulty_reason=item.get("difficulty_reason", ""),
            review_flags=[] if state == "confirmed" else flags, published_reason_flags=flags,
            content_review=content_review or None, title_review=title_review or None,
            tex_sha256=item["tex_sha256"], license=item.get("license", ""),
            license_path=item.get("license_path", ""), source_id=item.get("source_id", ""),
            source_url=item.get("source_url", ""), source_version=item.get("source_version", ""),
            item_path=item["item_path"], provenance_path=f"sources/{pid}/provenance.json",
            current_item_path=replacement.get("item_path", item["item_path"]),
            current_tex_sha256=replacement.get("tex_sha256", item["tex_sha256"]),
            current_pdf_path=replacement.get("pdf_path"),
            current_revision_status=replacement.get("status", "published_original"),
            publication_status="published_material"))
    return dict(schema_version=2, master_manifest="manifest.json", count=len(result),
                qualification_scope="Published material count is not a current scientific qualification count. H remains the historical label; confirmed_H requires a scoped content review.",
                published_difficulty_counts=dict(sorted(collections.Counter(x["published_H"] for x in result).items())),
                qualification_counts=dict(sorted(collections.Counter(x["qualification_status"] for x in result).items())),
                current_confirmed_difficulty_counts=dict(sorted(collections.Counter(x["confirmed_H"] for x in result if x["confirmed_H"]).items())),
                items=result)


def intervening_statement(source, statement, proof):
    if not statement or not proof or statement[1] >= proof[0]:
        return []
    gap = "\n".join(source.splitlines()[statement[1]:proof[0] - 1])
    gap = re.sub(r"(?<!\\)%[^\n]*", "", gap)
    return THM_ENV.findall(gap)


def attach_research(data, mappings, records):
    """Attach new reading evidence to existing IDs; never add a counted problem."""
    main = {row["problem_id"]: row for row in data["items"]}
    research = {row["problem_id"]: row for row in records}
    seen = set()
    for row in main.values():
        row["research_reviews"] = []
    for mapping in mappings:
        pid, rid = str(mapping["main_problem_id"]), mapping["research_id"]
        if pid not in main or rid not in research or (pid, rid) in seen:
            raise ValueError("unknown or duplicate research mapping: " + str((pid, rid)))
        seen.add((pid, rid)); record = research[rid]
        main[pid]["research_reviews"].append(dict(
            research_id=rid, difficulty_level=record.get("difficulty_level"),
            difficulty_reason=record.get("difficulty_reason"),
            selection_status=record.get("selection_status"),
            source_record=record.get("source_record"), review_evidence=record.get("review_evidence", []),
            review_flags=record.get("review_flags", []),
            scope="Additional reading evidence for the same source claim; no new count or automatic grade promotion."))
    data["research_linked_main_count"] = sum(bool(row["research_reviews"]) for row in main.values())
    data["research_evidence_link_count"] = len(seen)


def model_solution_headers(text):
    pattern = re.compile(r"\\begin\{(?:proof|solution|answer)\}\s*\[[^\]\n]*(?:GPT[- ]?\d|ChatGPT|DeepSeek|Claude|Gemini|LLM)[^\]\n]*\]", re.I)
    return [text.count("\n", 0, match.start()) + 1 for match in pattern.finditer(text)]


def scan_pairing(root, evidence):
    """Flag an intervening claim; explicit non-adjacent proofs still need reading."""
    findings = []
    cache = {}
    for pid, item in evidence["items"].items():
        bodies = item.get("bodies", [])
        statements = [x for x in bodies if x.get("role") == "primary_statement"]
        proofs = [x for x in bodies if x.get("role") == "primary_proof"]
        for statement in statements:
            for proof in proofs:
                for a in statement.get("spans", [statement]):
                    for b in proof.get("spans", [proof]):
                        if a.get("source_index") != b.get("source_index") or not a.get("source_lines") or not b.get("source_lines"):
                            continue
                        index = a.get("source_index")
                        sources = item.get("sources", [])
                        if not isinstance(index, int) or index >= len(sources):
                            continue
                        source = sources[index]
                        name = source.get("path")
                        if not name or source.get("root", "source") != "package":
                            continue
                        path = (root / "editable-corpus" / name).resolve()
                        if not path.is_relative_to((root / "editable-corpus").resolve()) or not path.is_file():
                            continue
                        if name not in cache:
                            cache[name] = path.read_text(encoding="utf-8-sig")
                        hit = intervening_statement(cache[name], a["source_lines"], b["source_lines"])
                        if hit:
                            findings.append(dict(problem_id=pid, issue="intervening_statement_before_selected_proof",
                                                 source_path="editable-corpus/" + name,
                                                 statement_lines=a["source_lines"], proof_lines=b["source_lines"],
                                                 intervening_environments=hit,
                                                 interpretation="Requires source-level pairing review; not an automatic rejection."))
        # Each source is normally specific to one item; do not retain a whole corpus in RAM.
        cache.clear()
    return findings


def md(value):
    return str(value or "").replace("|", "&#124;").replace("\n", " ")


def render_outputs(data):
    rows = data["items"]
    outputs = {"editable-corpus/catalog.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n"}
    buffer = io.StringIO(newline="")
    columns = ["problem_id", "arxiv_id", "version", "title", "author", "claim", "H", "confirmed_H", "qualification_status", "current_revision_status", "license", "current_item_path", "current_pdf_path", "current_tex_sha256", "item_path", "source_url", "tex_sha256"]
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    outputs["editable-corpus/catalog.csv"] = buffer.getvalue()
    lines = ["# 当前题目目录", "", f"共 **{len(rows):,} 条已发布材料**，每页最多500条，按稳定题号排序。历史评级不等于本轮确认合格；待返修题暂不用于训练或评测。",
             "", "完整机器目录：[JSON](catalog.json) · [CSV](catalog.csv)；历史交付索引：[INDEX](INDEX.md)；[返修说明](../curation/REPAIRS.md)。",
             "", "| 分页 | 题号范围 | 条数 |", "|---|---|---|"]
    chunks = [rows[start:start + 500] for start in range(0, len(rows), 500)]
    for number, chunk in enumerate(chunks, 1):
        page_name = f"{number:03d}.md"
        lines.append(f"| [第{number}页](catalog-pages/{page_name}) | {chunk[0]['problem_id']} — {chunk[-1]['problem_id']} | {len(chunk)} |")
        nav = ["[目录首页](../CORPUS_INDEX.md)"]
        if number > 1:
            nav.append(f"[上一页]({number-1:03d}.md)")
        if number < len(chunks):
            nav.append(f"[下一页]({number+1:03d}.md)")
        page = [f"# 题目目录 · 第{number}/{len(chunks)}页", "", " · ".join(nav), "",
                "历史评级不是本轮核准；待返修题暂不采用。支持上下文不单独计数。", "",
                "| 题号 | 当前题名 | 历史评级 | 本轮确认 | 内容状态 | TeX | 许可 |", "|---|---|---|---|---|---|---|"]
        for row in chunk:
            state = STATUS_ZH[row["qualification_status"]]
            if row["current_revision_status"] != "published_original":
                state += "；本地修订待合并"
            page.append("| " + " | ".join([row["problem_id"], md(row["title"]), row["published_H"], row["confirmed_H"] or "—",
                        state, f"[题证](../{row['current_item_path']})", f"[{md(row['license'])}](../{row['license_path']})"]) + " |")
        outputs["editable-corpus/catalog-pages/" + page_name] = "\n".join(page) + "\n"
    outputs["editable-corpus/CORPUS_INDEX.md"] = "\n".join(lines) + "\n"
    summary = {k: v for k, v in data.items() if k != "items"}
    summary["published_reason_flag_counts"] = dict(sorted(collections.Counter(f for x in rows for f in x["published_reason_flags"]).items()))
    summary["current_content_reviewed_count"] = sum(bool(x["content_review"]) for x in rows)
    summary["local_validated_revision_count"] = sum(x["current_revision_status"] == "local_validated_not_merged" for x in rows)
    summary["title_corrected_count"] = sum(x["title"] != x["published_title"] for x in rows)
    summary["nonempty_license_count"] = sum(bool(x["license"]) for x in rows)
    outputs["curation/SUMMARY.json"] = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    queue = [dict(problem_id=x["problem_id"], qualification_status=x["qualification_status"],
                  review_flags=x["review_flags"], issue=(x["content_review"] or {}).get("issue"))
             for x in rows if x["qualification_status"] in {"needs_review", "hold"}]
    outputs["curation/review-queue.jsonl"] = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in queue)
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--check", action="store_true", help="Compare generated bytes without writing")
    parser.add_argument("--scan-pairing", action="store_true", help="Also inspect original source intervals for intervening statements")
    args = parser.parse_args(); root = args.root.resolve()
    manifest = json.loads((root / "editable-corpus/manifest.json").read_text(encoding="utf-8-sig"))
    review_file = root / "curation/reviews.jsonl"
    reviews = [json.loads(line) for line in review_file.read_text(encoding="utf-8-sig").splitlines() if line.strip()] if review_file.exists() else []
    second_file = root / "curation/second-reviews.jsonl"
    if second_file.exists():
        content = {str(row["problem_id"]): row for row in reviews if row.get("review_scope") == "content"}
        seen = set()
        for line in second_file.read_text(encoding="utf-8-sig").splitlines():
            if not line.strip():
                continue
            second = json.loads(line); pid = str(second["problem_id"])
            if pid not in content or pid in seen:
                raise ValueError("unknown or duplicate second review: " + pid)
            seen.add(pid)
            content[pid]["second_review"] = second
            # A second opinion never silently turns a pending first review into admission.
    data = make_catalog(manifest["items"], reviews)
    mappings = root / "research-line/main-overlap.jsonl"
    records = root / "research-line/records.jsonl"
    if mappings.exists() and records.exists():
        attach_research(data,
                        [json.loads(line) for line in mappings.read_text(encoding="utf-8").splitlines() if line.strip()],
                        [json.loads(line) for line in records.read_text(encoding="utf-8").splitlines() if line.strip()])
    outputs = render_outputs(data)
    readme = root / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        summary = (f"当前公开材料 **{data['count']:,} 条**。这是已经交付的材料数，不代表每条都已按当前标准重新核准。\n\n"
                   f"当前目录覆盖全部题目，已修正 **{sum(x['title'] != x['published_title'] for x in data['items'])}** 个题名；"
                   f"明确待返修 **{data['qualification_counts'].get('hold', 0)}** 条。详见[返修说明](curation/REPAIRS.md)。")
        if "<!-- catalog-summary:start -->" in text:
            outputs["README.md"] = re.sub(r"(?s)(<!-- catalog-summary:start -->\n).*?(\n<!-- catalog-summary:end -->)",
                                          lambda match: match[1] + summary + match[2], text)
    if args.scan_pairing:
        evidence = json.loads((root / "editable-corpus/delivery-evidence.json").read_text(encoding="utf-8-sig"))
        findings = scan_pairing(root, evidence)
        outputs["curation/pairing-review.jsonl"] = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in findings)
        print("pairing review candidates:", len(findings))
        authorship = []
        for item in manifest["items"]:
            path = root / "editable-corpus" / item["item_path"]
            text = path.read_text(encoding="utf-8-sig")
            locations = model_solution_headers(text)
            if locations:
                authorship.append(dict(problem_id=item["problem_id"], issue="explicit_model_solution_header",
                                       path="editable-corpus/" + item["item_path"], lines=locations,
                                       interpretation="Check source attribution; a model-labelled proof is not a human-authored proof."))
        outputs["curation/authorship-review.jsonl"] = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in authorship)
        print("explicit model-solution headers:", len(authorship))
    different = []
    for name, text in outputs.items():
        path = root / name
        if args.check:
            if not path.exists() or path.read_bytes() != text.encode("utf-8"):
                different.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode("utf-8"))
    print(json.dumps({"count": data["count"], "qualification_counts": data["qualification_counts"], "stale_files": different}, ensure_ascii=False))
    return int(bool(different))


if __name__ == "__main__":
    raise SystemExit(main())
