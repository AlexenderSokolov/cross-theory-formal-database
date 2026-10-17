"""Reproduce source metadata aggregates from one exact Git manifest snapshot.

Stdlib only. Reads `git show SNAPSHOT:editable-corpus/manifest.json` and prints
JSON; never writes corpus, scoring, evidence, or output files. Material rows and
canonical work IDs do not establish independent claims, verified persons,
mathematical correctness, or delivery qualification. The preserved eleven-pair
assessment is separate evidence; this helper does not reread or compare proofs.
"""
import argparse
from collections import Counter
import json
import re
import subprocess
import sys


POLICY = "reviewed-revision-v2"
DOI = re.compile(r"10\.\d{4,9}/[^\s?#]+", re.IGNORECASE)
ARXIV = re.compile(r"(?:arxiv:|arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})(?:v\d+)?", re.IGNORECASE)
TAG = re.compile(r"https?://stacks\.math\.columbia\.edu/tag/([A-Za-z0-9]{4})(?![A-Za-z0-9])")
PROJECTS = (("stacks-project:", "work:Stacks-Project", "Stacks Project"),
            ("hott-book:", "work:HoTT-book", "HoTT book"),
            ("openlogic:", "work:OpenLogic", "Open Logic Project"),
            ("aljabr2:", "work:AlJabr-2", "AlJabr-2"))


def doi_id(value):
    """DOI in a recorded ID or URL, without revision/download locator suffixes."""
    match = DOI.search(value or "")
    if not match:
        return None
    identifier = match.group(0).split(":", 1)[0].rstrip("/").casefold()
    if identifier.endswith(".pdf"):
        identifier = identifier[:-4]
    return "doi:" + identifier


def arxiv_id(value):
    match = ARXIV.search(value or "")
    return "arxiv:" + match.group(1) if match else None


def canonical_work(row):
    """Work grouping only; source ID takes precedence over a retrieval URL."""
    source_id = row.get("source_id", "")
    for prefix, work, _ in PROJECTS:
        if source_id.casefold().startswith(prefix):
            return work
    return (doi_id(source_id) or arxiv_id(source_id)
            or doi_id(row.get("source_url", "")) or arxiv_id(row.get("source_url", "")))


def source_locator_identity(source_id):
    """Conservative locator identity: retain chapter filename and pinned revision.

    In particular, `morphisms.tex` and `stacks-morphisms.tex` are different
    chapters even though both contribute to the single Stacks work aggregate.
    Do not remove `stacks-`, `.tex`, versions, or snapshots from source locators.
    """
    return source_id.strip()


def family(row):
    source_id = row.get("source_id", "")
    for prefix, _, name in PROJECTS:
        if source_id.casefold().startswith(prefix):
            return name
    work = canonical_work(row)
    if work and work.startswith("arxiv:"):
        return "arXiv"
    if work and work.startswith("doi:"):
        identifier = work.removeprefix("doi:")
        if identifier.startswith("10.3842/sigma."):
            return "SIGMA"
        for journal in ("jep", "alco", "ahl", "afst"):
            if identifier.startswith("10.5802/" + journal + "."):
                return "Centre-Mersenne/" + journal
        return "DOI " + identifier.split("/", 1)[0]
    return "unresolved"


def explicit_aliases(rows):
    """Only a DOI source ID with an arXiv URL in that same manifest row."""
    return [(doi_id(row.get("source_id", "")), arxiv_id(row.get("source_url", "")))
            for row in rows if doi_id(row.get("source_id", ""))
            and arxiv_id(row.get("source_url", ""))]


def alias_map(pairs):
    parents = {}

    def find(identifier):
        parents.setdefault(identifier, identifier)
        while parents[identifier] != identifier:
            parents[identifier] = parents[parents[identifier]]
            identifier = parents[identifier]
        return identifier

    for doi, arxiv in pairs:
        a, b = find(doi), find(arxiv)
        # DOI labels first; deterministic canonical-ID order for ties.
        preferred, other = sorted((a, b), key=lambda key: (not key.startswith("doi:"), key))
        parents[other] = preferred
    return {identifier: find(identifier) for identifier in parents}


def summary(rows, aliases):
    works = Counter(aliases.get(work, work) for row in rows
                    if (work := canonical_work(row)) is not None)
    families = Counter(family(row) for row in rows)
    families = dict(sorted(families.items(), key=lambda pair: (-pair[1], pair[0])))
    top = sorted(works.items(), key=lambda pair: (-pair[1], pair[0]))[:10]
    stacks = [row for row in rows if family(row) == "Stacks Project"]
    tags_by_row = [TAG.findall(json.dumps(row, ensure_ascii=False)) for row in stacks]
    primary_tags, entry_tags = [], []
    primary_rows = entry_rows = 0
    for row in stacks:
        primary = row.get("primary", {})
        spans = [primary] if isinstance(primary, dict) else primary
        tags = [tag for span in spans for tag in TAG.findall(span.get("tag_url", ""))]
        primary_rows += bool(tags)
        primary_tags.extend(tags)
        tags = TAG.findall(row.get("source_url", ""))
        entry_rows += bool(tags)
        entry_tags.extend(tags)
    credit_strings = {credit for row in rows for credit in row.get("authors", [])
                      if isinstance(credit, str) and credit.strip()}
    year_counts = Counter("20" + work[6:8] for row in rows
                          if (work := arxiv_id(row.get("source_id", ""))))
    total = len(rows)
    percent = lambda count: round(100 * count / total, 6) if total else 0.0
    result = {
        "materials": total,
        "raw_source_ids": len({row.get("source_id", "") for row in rows}),
        "normalized_work_ids": len(works),
        "unresolved_rows": sum(canonical_work(row) is None for row in rows),
        "family_counts": families,
        "family_percent": {key: percent(count) for key, count in families.items()},
        "top10_works": [[key, count] for key, count in top],
        "concentration_percent": {str(n): percent(sum(count for _, count in top[:n])) for n in (1, 5, 10)},
        "stacks_rows": len(stacks),
        "stacks_rows_with_explicit_tag_url": sum(bool(tags) for tags in tags_by_row),
        "stacks_rows_without_explicit_tag_url": sum(not tags for tags in tags_by_row),
        "stacks_unique_explicit_tags": len({tag for tags in tags_by_row for tag in tags}),
        # Sum row-distinct explicit tag references, not repeated URL occurrences.
        "stacks_tag_reference_count": sum(len(set(tags)) for tags in tags_by_row),
        "author_field_nonempty_rows": sum(bool(row.get("author", "").strip()) for row in rows),
        "distinct_author_field_strings": len({row["author"] for row in rows if row.get("author", "").strip()}),
        "explicit_authors_list_rows": sum(isinstance(row.get("authors"), list) and bool(row["authors"]) for row in rows),
        "unique_explicit_authors_list_strings": len(credit_strings),
        # No structured year field exists in this manifest. Dates in citations,
        # retrieval fields or DOI strings are not publication-year fields.
        "structured_publication_year_rows": sum(bool(row.get("publication_year") or row.get("year")) for row in rows),
        "arxiv_identifier_year_counts": dict(sorted(year_counts.items())),
        "arxiv_identifier_year_rows": sum(year_counts.values()),
        "stacks_explicit_primary_tag_rows": primary_rows,
        "stacks_distinct_explicit_primary_tags": len(set(primary_tags)),
        "stacks_primary_tag_unknown_rows": len(stacks) - primary_rows,
        "stacks_source_entry_tag_rows": entry_rows,
        "stacks_distinct_source_entry_tags": len(set(entry_tags)),
        "review_state_counts": dict(sorted(Counter(row.get("review_state", "absent") for row in rows).items())),
    }
    for n in (1, 5, 10):
        result["top" + str(n) + "_count"] = sum(count for _, count in top[:n])
    return result


def statistics(rows, snapshot):
    pairs = explicit_aliases(rows)
    aliases = alias_map(pairs)
    strata = {"all": rows,
              "legacy": [row for row in rows if row.get("policy") != POLICY],
              "prepared": [row for row in rows if row.get("policy") == POLICY]}
    result = {"snapshot": snapshot,
              "method": "Manifest material rows; work IDs use source ID before URL, DOI casefold, arXiv version removal, and one work each for Stacks/HoTT/OpenLogic/AlJabr-2. Only explicit same-row DOI source ID/arXiv URL pairs are unioned. No title or inferred identity matching. Primary tags use primary.tag_url only; entry/reference tags remain separate. Author values are credit strings, not verified persons. arXiv identifier years are proxies, not publication years. Work grouping must not be used to erase chapter locator distinctions or change the preserved eleven-pair assessment.",
              "strata": {name: summary(items, aliases) for name, items in strata.items()},
              "explicit_alias_row_count": len(pairs),
              "explicit_alias_pair_count": len(set(pairs))}
    conflict = next((row for row in rows if str(row.get("problem_id")) == "900000403"), None)
    if conflict:
        # In-memory sensitivity only: retain DOI/work/URL/author and replace
        # this row's authors list with the two names in its manifest credit.
        corrected = [{**row, "authors": [part.strip() for part in row["author"].split(";")]}
                     if row is conflict else row for row in rows]
        after = summary(corrected, aliases)
        before = result["strata"]["all"]
        source_fields = ("family_counts", "normalized_work_ids", "raw_source_ids", "top10_works",
                         "top1_count", "top5_count", "top10_count")
        result["metadata_conflict_900000403_sensitivity"] = {
            "source_counts_unchanged": all(before[key] == after[key] for key in source_fields),
            "unique_explicit_authors_list_strings_before": before["unique_explicit_authors_list_strings"],
            "unique_explicit_authors_list_strings_after": after["unique_explicit_authors_list_strings"],
        }
    return result


def load_manifest(repo, snapshot):
    if not re.fullmatch(r"[0-9a-fA-F]{40}", snapshot):
        raise ValueError("snapshot must be a full 40-hex Git commit")
    process = subprocess.run(["git", "-C", str(repo), "show",
                              snapshot + ":editable-corpus/manifest.json"],
                             check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return json.loads(process.stdout.decode("utf-8"))["items"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True, help="full 40-hex Git commit")
    parser.add_argument("--repo", required=True, help="Git repository path")
    args = parser.parse_args()
    try:
        rows = load_manifest(args.repo, args.snapshot)
    except (ValueError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    json.dump(statistics(rows, args.snapshot.lower()), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
