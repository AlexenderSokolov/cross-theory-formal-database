"""Small, reproducible reading projections of existing author materials.

The manifest owns membership. The catalog supplies recorded review metadata;
neither this module nor its output assesses mathematics or invents subject tags.
Only navigation files are written. Source files and canonical metadata are read.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote, urlsplit

PAGE_ITEMS = 100
PAGE_BYTES = 64 * 1024


def text(value, limit=220):
    value = " ".join(str(value or "").split()).replace("|", "\\|")
    return value if len(value) <= limit else value[:limit - 1] + "…"


def relative(value):
    value = str(value or "").replace("\\", "/")
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or ":" in path.parts[0]:
        raise ValueError("reader path must stay inside the corpus: " + value)
    return path.as_posix()


def local_link(label, path, prefix="../../", fragment=""):
    return "[" + text(label, 60) + "](" + prefix + quote(relative(path), safe="/") + fragment + ")"


def source_link(url):
    url = str(url or "")
    if urlsplit(url).scheme not in ("http", "https"):
        return ""
    return "[作者来源](" + quote(url, safe=":/?=&%#@+;,~!$*'") + ")"


def registry_rows(corpus):
    path = Path(corpus) / "work-registry.jsonl"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8-sig") as stream:
        rows = [json.loads(line) for line in stream if line.strip()]
    return {row["work_key"]: row for row in rows}


def reading_links(row, registry):
    links = []
    if row.get("item_path"):
        links.append(local_link("题证／条目", row["item_path"]))
    reference = row.get("work_ref") or {}
    work = registry.get(reference.get("work_key"), {})
    root = work.get("public_root") or work.get("root")
    material = next((m for m in row.get("materials", []) if m.get("reader_path")), None)
    if material:
        label = "已有阅读PDF" if material["reader_path"].lower().endswith(".pdf") else "已有阅读材料"
        links.append(local_link(label, material["reader_path"]))
    if work.get("state") == "published" and root:
        reader = work.get("readability", {}).get("path")
        if not material and reader in work.get("files", []):
            label = "已有阅读PDF" if reader.lower().endswith(".pdf") else "已有阅读材料"
            links.append(local_link(label, relative(root) + "/" + relative(reader)))
        # Legacy entries without exact proof spans retain their original item link.
        for span in (row.get("proof_spans") or [])[:2]:
            path = span.get("path")
            path = work.get("path_aliases", {}).get(path, path)
            start, end = span.get("start_line"), span.get("end_line")
            if path in work.get("files", []) and isinstance(start, int) and isinstance(end, int) and 0 < start <= end:
                links.append(local_link("证明 L" + str(start) + "–" + str(end),
                                        relative(root) + "/" + relative(path),
                                        fragment="#L" + str(start) + "-L" + str(end)))
    return " · ".join(links)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def render_reader_files(corpus, manifest, catalog):
    """Return only derived UTF-8 text, without touching canonical inputs."""
    active = manifest["items"]
    ids = [row["problem_id"] for row in active]
    if any(not isinstance(ident, str) or not ident.isdecimal() for ident in ids):
        raise ValueError("reader IDs must be stable decimal strings")
    if len(ids) != len(set(ids)) or set(ids) & set(manifest.get("retired_problem_ids", [])):
        raise ValueError("reader membership contains duplicate or retired IDs")
    old = {row["problem_id"]: row for row in catalog.get("items", [])}
    registry = registry_rows(corpus)
    rows = []
    by_format = defaultdict(list)
    by_source = defaultdict(list)
    for number, original in enumerate(sorted(active, key=lambda row: row["problem_id"]), 1):
        prior = old.get(original["problem_id"], {})
        row = dict(original)
        row.update(display_index=number,
                   collection_state=prior.get("collection_state", "retained_material"),
                   difficulty_state=prior.get("difficulty_state", original.get("difficulty_state", "not_reassessed")))
        row["reader_format"] = "lean" if original.get("material_format") == "native_lean" else "tex"
        rows.append(row)
        by_format[row["reader_format"]].append(row)
        host = urlsplit(str(row.get("source_url") or "")).hostname or "未提供公开来源URL"
        by_source[host].append(row["problem_id"])
    outputs = {}
    pages = []
    id_page = {}
    header = ("| 展示序号 | 稳定题号 | 题名 | 标签／记录状态 | 题证与证明位置 | 来源 |\n"
              "|---|---|---|---|---|---|\n")

    def markdown_row(row):
        values = [row["display_index"], row["problem_id"], row.get("title"),
                  str(row.get("difficulty_level") or "未标") + " / " + str(row["difficulty_state"]),
                  reading_links(row, registry), source_link(row.get("source_url"))]
        return "| " + " | ".join(text(value, 320) if i not in (4, 5) else str(value)
                                 for i, value in enumerate(values)) + " |\n"

    def compact_row(row):
        # Full canonical titles and evidence stay at their original locations.
        return {"problem_id": row["problem_id"], "title": text(row.get("title"), 1000),
                "material_format": row.get("material_format", "legacy_tex"),
                "difficulty_label": row.get("difficulty_level"),
                "difficulty_state": row["difficulty_state"], "collection_state": row["collection_state"],
                "item_path": row.get("item_path"), "source_url": row.get("source_url"),
                "source_id": row.get("source_id"), "source_version": row.get("source_version")}

    for kind in ("tex", "lean"):
        chunks = []
        chunk = []
        md_size, js_size = len(header.encode("utf-8")), 3
        for row in by_format[kind]:
            row_md = len(markdown_row(row).encode("utf-8"))
            row_js = len(json_text([compact_row(row)]).encode("utf-8"))
            if chunk and (len(chunk) >= PAGE_ITEMS or max(md_size + row_md, js_size + row_js) > PAGE_BYTES - 2048):
                chunks.append(chunk)
                chunk = [row]
                md_size, js_size = len(header.encode("utf-8")) + row_md, 3 + row_js
            else:
                chunk.append(row)
                md_size += row_md
                js_size += row_js
        if chunk:
            chunks.append(chunk)
        navigation = ["# " + ("Lean" if kind == "lean" else "TeX") + " 材料", "",
                      "[目录首页](../README.md) · [按来源浏览](../sources.md)", "",
                      "每行是一个活动问题；标签沿用既有记录，不表示重新数学认证。", "",
                      "| 分页 | 条数 | 稳定题号范围 |", "|---|---|---|"]
        for i, chunk in enumerate(chunks, 1):
            stem = str(i).zfill(3)
            path = "browse/" + kind + "/" + stem
            page_ids = [row["problem_id"] for row in chunk]
            nav = ["[本格式目录](README.md)", "[总入口](../README.md)"]
            if i > 1:
                nav.append("[上一页](" + str(i - 1).zfill(3) + ".md)")
            if i < len(chunks):
                nav.append("[下一页](" + str(i + 1).zfill(3) + ".md)")
            nav.append("[本页JSON](" + stem + ".json)")
            page = ("# " + kind.upper() + " 材料 · 第 " + str(i) + " 页\n\n" + " · ".join(nav) +
                    "\n\n题名可能缩略；完整题证、定位和先修请打开条目。\n\n" + header +
                    "".join(markdown_row(row) for row in chunk))
            data = json_text([compact_row(row) for row in chunk])
            if max(len(page.encode("utf-8")), len(data.encode("utf-8"))) > PAGE_BYTES:
                raise ValueError("one reader record exceeds the small-page budget: " + page_ids[0])
            outputs[path + ".md"], outputs[path + ".json"] = page, data
            pages.append({"path": path + ".md", "json_path": path + ".json", "format": kind,
                          "count": len(chunk), "problem_ids": page_ids})
            id_page.update({ident: path + ".md" for ident in page_ids})
            navigation.append("| [" + stem + "](" + stem + ".md) · [JSON](" + stem + ".json) | " +
                              str(len(chunk)) + " | " + page_ids[0] + " – " + page_ids[-1] + " |")
        if not chunks:
            navigation.append("\n当前没有此格式的活动材料。")
        outputs["browse/" + kind + "/README.md"] = "\n".join(navigation) + "\n"

    format_counts = {kind: len(by_format[kind]) for kind in ("tex", "lean")}
    summary = {"schema_version": 1, "membership_basis": "manifest.json:items",
               "material_count": len(rows), "format_counts": format_counts,
               "difficulty_state_counts": dict(sorted(Counter(r["difficulty_state"] for r in rows).items())),
               "page_max_items": PAGE_ITEMS, "page_max_bytes": PAGE_BYTES, "pages": pages,
               "scope": "Recorded author materials; no new difficulty, cross-theory or mathematical verification."}
    # The compact summary does not duplicate every ID. Per-page JSON owns those lists.
    summary["pages"] = [{k: v for k, v in page.items() if k != "problem_ids"} for page in pages]
    outputs["browse/summary.json"] = json_text(summary)
    sources = ["# 按作者来源浏览", "", "[目录首页](README.md)", "",
               "仅按原记录的公开来源主机归组；不是学科标签或跨理论判断。", "",
               "| 来源主机 | 材料数 | 涉及的目录页 |", "|---|---|---|"]
    for host, members in sorted(by_source.items()):
        paths = sorted({id_page[ident] for ident in members})
        links = " · ".join("[" + p.split("/")[1] + "/" + Path(p).stem + "](" + p[7:] + ")" for p in paths)
        sources.append("| " + text(host) + " | " + str(len(members)) + " | " + links + " |")
    outputs["browse/sources.md"] = "\n".join(sources) + "\n"
    outputs["browse/README.md"] = ("# 题库阅读入口\n\n"
        f"当前活动材料 **{len(rows):,}** 条：TeX **{format_counts['tex']:,}** 条，Lean **{format_counts['lean']:,}** 条。\n\n"
        "活动材料数、记录中的难度筛选状态、数学正确性和跨理论标注是不同概念。历史 H 标签不表示已按当前标准重新核准。\n\n"
        "| 阅读目的 | 入口 |\n|---|---|\n"
        "| 从可读小页选题 | [TeX目录](tex/README.md) · [Lean目录](lean/README.md) |\n"
        "| 按作者来源缩小范围 | [来源目录](sources.md) |\n"
        "| 程序或网页工具分段读取 | 每页配套JSON；[精简统计与分页位置](summary.json) |\n"
        "| 下载全量元数据 | [catalog.json](../catalog.json) · [catalog.csv](../catalog.csv) |\n\n"
        "## 怎样读一道题\n\n"
        "1. 打开目录行中的题证／条目；旧TeX包直接给出正文，新共享条目给出固定作品与题面、证明、上下文范围。\n"
        "2. 有已有阅读PDF或证明行链接时直接打开；必要定义、专门支撑引理仍以条目原记录为准。\n"
        "3. Lean保持原源码、工具链与运行状态；未运行不等于缺失，也不能称为已验证。TeX篇幅以实际原文或PDF为准。\n\n"
        "## 给网页端GPT与合作者\n\n"
        "先提供本页与选题要求，再沿格式目录读取相关分页和每页JSON；不要一次要求抓取巨大manifest或全量catalog。"
        "题名关键词只用于初筛，入选前实际阅读题面、完整作者证明和必要上下文。每页最多100条且MD/JSON不超过64 KiB。"
        "当前目录不自动判断学科或跨理论；证明深度不能只看长度、标签或Lean imports。\n\n"
        "使用Git固定版本链接记录所选题；链接无法读取时只补对应分页或题证文件，无需上传整个仓库。"
        "作者负责原数学，本项目整理来源与材料；明确缺口应如实保留，不由模型补证。\n\n"
        "## 维护\n\n"
        "此目录由现有活动材料投影入口统一生成。[生成与检查命令](../../run_reader_catalog.sh)；"
        "[开发说明](../../PROJECT.md)。不要手改分页或把总库导航输入旧逐题包合并器。\n")
    outputs["INDEX.md"] = ("# 当前材料索引\n\n"
        f"活动材料：**{len(rows):,}**。稳定题号保留；总清单已改为小型入口。\n\n"
        "- [开始阅读与选题](browse/README.md)\n- [TeX分页](browse/tex/README.md)\n"
        "- [Lean分页](browse/lean/README.md)\n- [按来源浏览](browse/sources.md)\n"
        "- [分片元数据与统计](browse/summary.json)\n- [完整JSON](catalog.json) · [完整CSV](catalog.csv)\n\n"
        "历史难度标签、材料完整性和实际运行状态分别记录；目录更新不执行数学认证。\n")
    outputs["CORPUS_INDEX.md"] = ("# 题库目录兼容入口\n\n"
        "本路径保留给已有引用，内容与当前材料投影同步。\n\n[当前索引](INDEX.md) · "
        "[阅读与选题](browse/README.md) · [来源目录](browse/sources.md)\n")
    outputs["README.md"] = ("# 数学作者题证材料\n\n"
        "[当前阅读入口](browse/README.md) · [TeX](browse/tex/README.md) · [Lean](browse/lean/README.md)\n\n"
        "题证按稳定问题编号关联固定版本作者材料；旧逐题包与新共享作品并存，目录统一展示。"
        "活动身份以manifest为准，机器目录、分页和展示编号是投影。\n\n"
        "阅读从小型目录开始；[完整元数据](catalog.json)、[作品注册表](work-registry.jsonl)及"
        "[数据库恢复说明](RECOVERY_CURRENT.md)按需使用。恢复或构建成功不表示新的数学判定。\n")
    # Material retirement or smaller partitions can leave formerly linked pages.
    # Replace those derived pages with a current-entry notice, without deleting
    # any files or carrying retired records into the active reading projection.
    for name in catalog.get("reader_files", []):
        if name not in outputs and re.fullmatch(r"browse/(tex|lean)/[0-9]+\.(md|json)", name):
            outputs[name] = ("# 此分页已退出当前目录\n\n[当前阅读入口](../README.md)。"
                             "历史内容请按原Git版本查看。\n" if name.endswith(".md") else
                             json_text({"status": "superseded_reader_page", "current_index": "../README.md"}))
    return outputs


def write_reader_catalog(corpus, manifest, catalog):
    corpus = Path(corpus)
    outputs = render_reader_files(corpus, manifest, catalog)
    for relative_path, content in outputs.items():
        path = corpus / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return sorted(outputs)


def check_reader_links(corpus, outputs):
    """Check committed file locations without downloading all author projects."""
    corpus = Path(corpus).resolve()
    root = corpus.parent
    tracked = set(subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"],
                                         text=True, encoding="utf-8").split("\0"))
    documents = {corpus / name: content for name, content in outputs.items() if name.endswith(".md")}
    for name in ("README.md", "PROJECT.md"):
        if (root / name).is_file():
            documents[root / name] = (root / name).read_text(encoding="utf-8-sig")
    missing, targets = {}, set()
    for document, content in documents.items():
        for href in re.findall(r"\[[^\]]*\]\(([^\n)]*)\)", content):
            if urlsplit(href).scheme or href.startswith("#"):
                continue
            target = (document.parent / unquote(href.split("#", 1)[0])).resolve()
            if not target.is_relative_to(root):
                missing[href] = "outside repository"
                continue
            name = target.relative_to(root).as_posix()
            targets.add(name)
            if name not in tracked and not target.is_file():
                missing[name] = document.relative_to(root).as_posix()
    if missing:
        raise ValueError("reader links do not name retained files: " + json.dumps(dict(list(missing.items())[:8]), ensure_ascii=False))
    return {"distinct_local_targets": len(targets), "missing_local_targets": 0,
            "scope": "Git file locations and generated navigation; not a build, mathematical review or remote fetch."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-links", action="store_true", help="also check retained Git paths; requires a repository checkout")
    args = parser.parse_args()
    if args.check_links and not args.check:
        parser.error("--check-links requires --check")
    manifest = json.loads((args.corpus / "manifest.json").read_text(encoding="utf-8-sig"))
    catalog = json.loads((args.corpus / "catalog.json").read_text(encoding="utf-8-sig"))
    if args.check:
        indexed = {row["problem_id"]: row for row in catalog["items"]}
        if set(indexed) != {row["problem_id"] for row in manifest["items"]} or catalog.get("count") != len(indexed):
            raise SystemExit("catalog membership differs from active manifest; regenerate with the normal projection entry")
        for row in manifest["items"]:
            if any(indexed[row["problem_id"]].get(key) != row.get(key) for key in ("title", "item_path", "source_url")):
                raise SystemExit("catalog metadata differs from manifest: " + row["problem_id"])
        outputs = render_reader_files(args.corpus, manifest, catalog)
        stale = [name for name, content in outputs.items() if not (args.corpus / name).is_file()
                 or (args.corpus / name).read_text(encoding="utf-8-sig") != content]
        if stale:
            raise SystemExit("reader projections missing or stale: " + ", ".join(stale[:8]))
    else:
        from prepared_retirements import write_active_indexes
        catalog = write_active_indexes(args.corpus, manifest, catalog)
        outputs = render_reader_files(args.corpus, manifest, catalog)
    result = {"status": "current" if args.check else "generated",
              "material_count": len(manifest["items"]), "files": len(outputs)}
    if args.check_links:
        result["links"] = check_reader_links(args.corpus, outputs)
    print(json_text(result).strip())


if __name__ == "__main__":
    main()
