#!/usr/bin/env python3
"""Drive one bounded author-material publication batch end to end (local side).

plan -> reserve -> adopt-material -> prepare  (on the host)
-> local CAS relay push -> host restore-only reconcile
-> worklist / STATUS / batch-result close-out.

The host stays the only writer of the production queue; this script never edits
production state directly.
"""
import argparse
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path

LOCAL = Path("C:/Users/20600/Documents/Codex/corpus-repair-20261010")
P = LOCAL / "research-line" / "harness-ready-20261011"
OPS = P / "operations"
WL = P / "PREPARATION_WORKLIST.jsonl"
R = "/disks/sata1/yupeng/human-proof-corpus/operations/codex-takeover-01a12558/corpus-repair-20261010"
ROP = R + "/research-line/harness-ready-20261011/operations"
PY = "/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python"
ALIAS = "Yupeng-orx"
SSHOPT = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o", "ProxyCommand=none",
          "-o", "ProxyJump=none", "-o", "ClearAllForwardings=yes"]
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")


def run(argv, cwd=None, timeout=2400, check=True):
    res = subprocess.run(argv, cwd=cwd, env=ENV, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=timeout)
    if check and res.returncode != 0:
        raise SystemExit("FAILED %s\nSTDOUT:\n%s\nSTDERR:\n%s" % (argv[:3], res.stdout[-3000:], res.stderr[-3000:]))
    return res


def ssh(cmd, timeout=2400, check=True):
    return run(["ssh", *SSHOPT, ALIAS, cmd], timeout=timeout, check=check)


def scp_down(remote, local):
    run(["scp", *SSHOPT, ALIAS + ":" + remote, str(local)])


def scp_up(local, remote):
    run(["scp", *SSHOPT, str(local), ALIAS + ":" + remote])


def load(p):
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


def save(p, obj):
    p = Path(p)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-id", required=True)
    ap.add_argument("--count", type=int, default=100)
    ap.add_argument("--defer", default="")
    ap.add_argument("--close-only", action="store_true",
                    help="skip plan/reserve/adopt/prepare/relay and only reconcile records for an already published batch")
    args = ap.parse_args()
    batch = args.batch_id
    if args.close_only:
        if not (OPS / (batch + "-plan.json")).exists():
            scp_down("%s/%s-publication.json" % (ROP, batch), OPS / (batch + "-publication.json"))
            spec = load(OPS / (batch + "-publication.json"))
            jobs = [{"task_id": p.rstrip("/").split("/")[-2], "revision": p.rstrip("/").split("/")[-1]}
                    for p in spec["job_paths"]]
            plan = {"batch_id": batch, "base_commit": spec["public_base_commit"], "base_count": None,
                    "jobs": jobs, "reconciliation_count": len(spec.get("source_reconciliations", [])),
                    "deferred_task_ids": [], "fresh_sources": []}
            save(OPS / (batch + "-plan.json"), plan)
        plan = load(OPS / (batch + "-plan.json"))
        return close_out(batch, plan, None)

    print("[1/6] plan", flush=True)
    out = ssh("cd %s && %s research-line/harness-ready-20261011/operations/author_material_batch.py "
              "--batch-id %s --count %d --defer '%s'" % (R, PY, batch, args.count, args.defer)).stdout
    print("   ", out.strip().splitlines()[0])
    scp_down("%s/%s-plan.json" % (ROP, batch), OPS / (batch + "-plan.json"))
    scp_down("%s/%s-relay.json" % (ROP, batch), OPS / (batch + "-relay.json"))
    plan = load(OPS / (batch + "-plan.json"))
    print("    jobs=%d reconciliations=%d new_sources=%d" %
          (len(plan["jobs"]), plan["reconciliation_count"], len(plan["fresh_sources"])))
    if not plan["jobs"]:
        print("    nothing selectable right now (every pending row is deferred); stopping before reserve")
        return 0

    print("[2/6] reserve", flush=True)
    res = ssh("cd %s && %s corpus-work/scripts/prepared_publish.py reserve --spec %s/%s-reserve.json"
              % (R, PY, ROP, batch), check=False)
    if res.returncode != 0:
        raise SystemExit("reserve failed:\n" + res.stdout[-2000:] + res.stderr[-2000:])
    print("    reserved/returned problem_ids:", res.stdout.count('"problem_id"'))

    print("[3/6] adopt-material", flush=True)
    res = ssh("bash %s/%s-adopt.sh" % (ROP, batch), check=False)
    tail = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""
    print("   ", tail)
    if "failed=0" not in tail:
        raise SystemExit("adopt failed:\n" + res.stdout[-3000:])

    print("[4/6] prepare", flush=True)
    res = ssh("cd %s && %s corpus-work/scripts/prepared_publish.py prepare --spec %s/%s-publication.json"
              % (R, PY, ROP, batch), check=False)
    if res.returncode != 0 or "candidate_commit" not in res.stdout:
        raise SystemExit("prepare failed:\n" + res.stdout[-2500:] + res.stderr[-2500:])
    prepared = json.loads(res.stdout[res.stdout.index("{"):])
    print("    candidate=%s material_count=%s increment=%s integrity=%s" %
          (prepared["candidate_commit"][:12], prepared["material_count"], prepared["increment"],
           prepared["sql"]["integrity"]))

    print("[5/6] local CAS relay + host restore", flush=True)
    # 推送前再探一次网络（Lead §2.2/§25.2「先验后用、探针靠近推送那一刻」）：
    # 开批时启动器已探过一次，但推送在 plan/reserve/adopt/prepare 之后（约 2-4 分钟），链路会抖。
    # 规则：直连能用 ⇒ 本次调用禁用代理；否则走配置代理（已活的那条）；两条都不通 ⇒ 拒开批
    #（本批此时已 prepared，不新建批号，日后只需重跑 relay + --close-only）。
    try:
        _spec = json.loads((OPS / (batch + "-relay.json")).read_text(encoding="utf-8"))
        _relay = str(_spec["relay_git_dir"])

        def _reach(argv):
            try:
                return subprocess.run(argv, capture_output=True, timeout=60).returncode == 0
            except Exception:
                return False

        _ls = ["git", "-C", _relay, "ls-remote", "origin", "refs/heads/main"]
        if _reach(["git", "-C", _relay, "-c", "http.proxy=", "-c", "https.proxy=", "ls-remote", "origin", "refs/heads/main"]):
            ENV["GIT_CONFIG_COUNT"] = "2"
            ENV["GIT_CONFIG_KEY_0"] = "http.proxy"
            ENV["GIT_CONFIG_VALUE_0"] = ""
            ENV["GIT_CONFIG_KEY_1"] = "https.proxy"
            ENV["GIT_CONFIG_VALUE_1"] = ""
            print("    推送路径探测：直连可用（本次调用禁用代理）", flush=True)
        elif _reach(_ls):
            for _k in ("GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0", "GIT_CONFIG_KEY_1", "GIT_CONFIG_VALUE_1"):
                ENV.pop(_k, None)
            print("    推送路径探测：直连不通、走配置代理可用", flush=True)
        else:
            raise SystemExit("推送路径两条都不通（直连与被配置的代理都失败）——拒开批；本批已 prepared，"
                             "不新建批号，链路恢复后只重跑 relay + --close-only 即可")
    except SystemExit:
        raise
    except Exception as _exc:
        print("    推送路径探测跳过（不阻断）：%s" % _exc, flush=True)
    state = None
    for attempt in range(1, 7):
        res = run([sys.executable, "prepared_remote.py", "--spec", str(OPS / (batch + "-relay.json"))],
                  cwd=str(LOCAL / "corpus-work" / "scripts"), check=False, timeout=1800)
        print("    relay attempt %d rc=%d" % (attempt, res.returncode))
        if res.returncode == 0:
            state = json.loads(res.stdout[res.stdout.index("{"):])
            break
        print("   ", (res.stdout + res.stderr).strip()[-400:])
        time.sleep(25)
    if state is None:
        raise SystemExit("relay did not reconcile after 6 attempts")
    server = state.get("server_result") or {}
    print("    reconciled commit=%s material_count=%s qualified=%s" %
          ((server.get("verified_corpus_commit") or state.get("verified_corpus_commit", ""))[:12],
           server.get("material_count"), server.get("current_qualified_count")))

    print("[6/6] close-out", flush=True)
    return close_out(batch, plan, None)   # authoritative numbers come from the host publication.json


def close_out(batch, plan, state):
    """Reconcile worklist / STATUS / batch-result for an already reconciled batch."""
    scp_down("%s/publication/%s/publication.json" % (R + "/research-line/harness-ready-20261011", batch),
             OPS / (batch + "-publication-state.json"))
    pub = load(OPS / (batch + "-publication-state.json"))
    if state is None:
        assert pub.get("stage") == "reconciled", pub.get("stage")
        state = {"verified_corpus_commit": pub["verified_corpus_commit"], "material_count": pub["material_count"],
                 "current_qualified_count": pub.get("current_qualified_count"),
                 "current_qualified_prepared": pub.get("current_qualified_prepared")}
    commit = state["verified_corpus_commit"]
    restored = pub.get("public_restore_result")
    restore = None
    if restored:
        local_restore = OPS / (batch + "-RESTORE_RESULT.json")
        scp_down(restored, local_restore)
        restore = load(local_restore)
    # Formal IDs come from the adopted jobs themselves; some worklist rows never
    # recorded the reserved number, so the worklist is filled from the same source.
    res = ssh("%s %s/batch_job_ids.py %s/%s-publication.json" % (PY, ROP, ROP, batch))
    ident = json.loads(res.stdout.strip().splitlines()[-1])
    rows = [json.loads(l) for l in io.open(WL, encoding="utf-8")]
    wanted = {(j["task_id"], j["revision"]) for j in plan["jobs"]}
    ids = []
    for r in rows:
        if (r["task_id"], r["revision"]) in wanted:
            assert r["state"] in ("prepared_unpublished", "published"), (r["task_id"], r["state"])
            formal = ident[r["task_id"] + "/" + r["revision"]]
            if r.get("problem_id") in (None, ""):
                r["problem_id"] = formal
            assert r["problem_id"] == formal, (r["task_id"], r["problem_id"], formal)
            if r["state"] == "published" and r.get("publication_commit") == commit:
                ids.append(r["problem_id"])
                continue
            r["state"] = "published"
            r["publication_commit"] = commit
            r["publication_batch"] = batch
            r["published_at"] = pub.get("completed_at")
            ids.append(r["problem_id"])
    assert len(ids) == len(plan["jobs"]), (len(ids), len(plan["jobs"]))
    tmp = WL.with_suffix(".jsonl.tmp")
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, WL)
    st = load(P / "STATUS.json")
    st["current_public_commit"] = commit
    st["current_material_count"] = state["material_count"]
    st["current_qualified_count"] = state.get("current_qualified_count")
    st["current_qualified_prepared_count"] = state.get("current_qualified_prepared")
    st["task_state_counts"] = {k: sum(1 for r in rows if r.get("state") == k) for k in
                               sorted({r.get("state") for r in rows})}
    st["ready_unpublished_formal_tasks"] = sum(1 for r in rows if r.get("state") == "prepared_unpublished" and r.get("handoff_slot") == "formal")
    st["ready_unpublished_reserve_tasks"] = sum(1 for r in rows if r.get("state") == "prepared_unpublished" and r.get("handoff_slot") == "reserve")
    st["prepared_unpublished_materials"] = st["task_state_counts"].get("prepared_unpublished", 0)
    st["deepseek_session_public_deliveries"] = int(st.get("deepseek_session_public_deliveries", 0)) + len(ids)
    st["latest_batch"] = {"batch_id": batch, "public_commit": commit, "public_increment": len(ids),
                          "result": "operations/%s-result.json" % batch}
    st["updated_at"] = time.strftime("%Y-%m-%d")
    save(P / "STATUS.json", st)
    result = {"schema_version": 1, "batch_id": batch, "policy": "reviewed-revision-v2",
              "preparation_basis": "author_material_collection", "completed_at": pub.get("completed_at"),
              "public_commit": commit, "public_base_commit_before": plan["base_commit"],
              "material_count_before": plan.get("base_count") or (state["material_count"] - len(ids)),
              "material_count_after": state["material_count"],
              "public_increment": len(ids), "problem_ids": sorted(ids),
              "current_qualified_count": state.get("current_qualified_count"),
              "current_qualified_prepared": state.get("current_qualified_prepared"),
              "restore_result": restored, "restore_status": (restore or {}).get("status"),
              "restored_prepared_jobs": (restore or {}).get("restored_prepared_jobs"),
              "adoption": "adopt-material reused the finished author TeX/PDF and author sources; no re-assembly, no recompilation",
              "source_reconciliations": plan["reconciliation_count"],
              "deferred_task_ids": plan.get("deferred_task_ids", []),
              "fresh_source_rows": [s for s, _ in plan["fresh_sources"]]}
    save(OPS / (batch + "-result.json"), result)
    scp_up(WL, R + "/research-line/harness-ready-20261011/PREPARATION_WORKLIST.jsonl")
    scp_up(P / "STATUS.json", R + "/research-line/harness-ready-20261011/STATUS.json")
    scp_up(OPS / (batch + "-result.json"), ROP + "/")
    print("    published %d | M=%s | Q=%s | remaining stock=%s" %
          (len(ids), state["material_count"], state.get("current_qualified_count"),
           st["prepared_unpublished_materials"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
